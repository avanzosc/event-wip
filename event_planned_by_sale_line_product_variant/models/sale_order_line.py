# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(SaleOrderLine, self).onchange_product_tmpl_id()
        if 'domain' not in res:
            res['domain'] = {}
        cond = res['domain'].get('product_id', [])
        cond.append(('categ_id', '=', self.product_category.id))
        res['domain']['product_id'] = cond
        return res
