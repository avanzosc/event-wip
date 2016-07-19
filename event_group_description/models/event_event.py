# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.model
    def create(self, vals):
        sale_line_obj = self.env['sale.order.line']
        if vals.get('sale_order_line', False):
            line = sale_line_obj.browse(vals.get('sale_order_line'))
            vals['name'] = line.group_description
        event = super(EventEvent, self).create(vals)
        return event
