# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    @api.multi
    @api.depends('customer_id', 'customer_id.street', 'customer_id.street2',
                 'customer_id.zip', 'customer_id.city')
    def _compute_customer_info(self):
        for presence in self:
            presence.customer_street = u"{} {} {} {}".format(
                presence.customer_id.street or '',
                presence.customer_id.street2 or '', presence.customer_id.zip or
                '', presence.customer_id.city or '')

    customer_id = fields.Many2one(
        comodel_name='res.partner', string='Customer',
        related='event.sale_order.partner_shipping_id', store=True)
    customer_street = fields.Char(
        string='Customer street', compute='_compute_customer_info', store=True)
