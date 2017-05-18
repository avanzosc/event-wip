# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_payer = fields.Selection(
        related='sale_order_id.payer', string='Invoice payer',
        store=True)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    invoice_state = fields.Selection(
        related='invoice_id.state', string='Invoice state', store=True)
    invoice_sale_order_id = fields.Many2one(
        comodel_name='sale.order', string='sale order',
        related='invoice_id.sale_order_id', store=True)
    invoice_payer = fields.Selection(
        related='invoice_sale_order_id.payer', string='Invoice payer',
        store=True)
    invoice_date_invoice = fields.Date(
        related='invoice_id.date_invoice', string='Invoice date',
        store=True)
