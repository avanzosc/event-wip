# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    student = fields.Many2one(
        comodel_name='res.partner', related='ml_inv_ref.student', store=True,
        string='Student')
    event_address_id = fields.Many2one(
        comodel_name='res.partner', related='ml_inv_ref.event_address_id',
        store=True, string='Event address')
    event_id = fields.Many2one(
        comodel_name='event.event', related='ml_inv_ref.event_id', store=True,
        string='Event')
    sale_order_id = fields.Many2one(
        comodel_name='sale.order', related='ml_inv_ref.sale_order_id',
        store=True, string='Sale order')
