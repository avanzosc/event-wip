# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ticket_event_product_ids = fields.Many2many(
        comodel_name='product.product', relation='rel_ticket_products',
        column1='product_id', column2='ticket_product_id',
        string='Ticket products', domain="[('event_ok','=',True)]",
        help='When the event is created by selling this product, this products'
        ' will be used for ticket creation.')
