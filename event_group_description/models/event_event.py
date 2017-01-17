# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.multi
    def _compute_count_sale_lines(self):
        for event in self:
            event.count_sale_lines = len(event.sale_order_line)

    group_description = fields.Char(
        string='Group description',
        related='sale_order_line.group_description')
    count_sale_lines = fields.Integer(
        string='Sale lines', compute='_compute_count_sale_lines')

    @api.model
    def create(self, vals):
        if vals.get('sale_order_line', False):
            line = self.env['sale.order.line'].browse(vals['sale_order_line'])
            vals['name'] = line.group_description
        event = super(EventEvent, self).create(vals)
        return event

    @api.multi
    def show_sale_lines(self):
        self.ensure_one()
        if self.sale_order_line:
            return {'name': _('Sale order lines'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'sale.order.line',
                    'domain': [('id', '=', self.sale_order_line.id)]}
