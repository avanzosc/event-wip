# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        if self.env.context.get('product_category', False):
            vals['product_category'] = self.env.context.get('product_category')
            vals['payer'] = self.env.context.get('payer')
        return super(SaleOrder, self).create(vals)
