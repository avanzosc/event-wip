# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields


class TestSaleOrderRenovateEvent(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderRenovateEvent, self).setUp()
        self.account_model = self.env['account.analytic.account']
        self.sale_model = self.env['sale.order']
        self.today = fields.Date.from_string(fields.Date.today())
        account_vals = {'name': 'Renovate event',
                        'date_start': "{}-01-01".format(int(self.today.year) -
                                                        1),
                        'date': "{}-12-31".format(int(self.today.year) -
                                                  1),
                        'state': 'open',
                        'type': 'contract',
                        'recurring_invoices': True,
                        'use_tasks': True}
        self.account = self.account_model.create(account_vals)
        self.env['project.project'].create(
            {'name': 'Renovate event', 'analytic_account_id': self.account.id})
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        sale_vals = {
            'name': 'sale order renovate event',
            'partner_id': self.ref('base.res_partner_1'),
            'project_id': self.account.id
        }
        sale_line_vals = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price,
            'performance': self.service_product.performance}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)
        self.event = self.browse_ref('event.event_0')
        self.event.sale_order = self.sale_order

    def test_sale_order_renovate_event(self):
        self.sale_order.automatic_renovate_contract_event()
        cond = [('generated_from_sale_order', '=', self.sale_order.id)]
        new_sale = self.sale_model.search(cond, limit=1)
        self.assertEquals(len(new_sale), 1, 'New sale no generated')
        self.assertEquals(self.sale_order.project_id.state, 'close',
                          'Bad state for old contract')
        self.assertEquals(new_sale.project_id.state, 'open',
                          'Bad state for new contract')
