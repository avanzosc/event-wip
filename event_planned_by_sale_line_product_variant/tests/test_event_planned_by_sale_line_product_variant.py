# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventPlannedBySaleLineProductVariant(common.TransactionCase):

    def setUp(self):
        super(TestEventPlannedBySaleLineProductVariant, self).setUp()
        self.sale_model = self.env['sale.order']
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        sale_vals = {
            'name': 'sale order 2000',
            'partner_id': self.ref('base.res_partner_1'),
        }
        sale_line_vals = {
            'product_tmpl_id': self.service_product.product_tmpl_id.id,
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price,
            'performance': self.service_product.performance,
            'product_category': self.service_product.categ_id.id}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_event_planned_by_sale_line_product_variant(self):
        res = self.sale_order.order_line[0].onchange_product_tmpl_id()
        domain = res.get('domain').get('product_id')
        cond = "('categ_id', '=', " + str(self.service_product.categ_id.id)
        self.assertNotIn(cond, domain, 'Bad domain on change product_tmpl_id')
