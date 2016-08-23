# -*- coding: utf-8 -*-
# (c) 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta
import time


class TestEventPlannedBySaleLine(common.TransactionCase):

    def setUp(self):
        super(TestEventPlannedBySaleLine, self).setUp()
        self.task_model = self.env['project.task']
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.project_model = self.env['project.project']
        self.event_model = self.env['event.event']
        self.task_model = self.env['project.task']
        self.procurement_model = self.env['procurement.order']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.registration_model = self.env['event.registration']
        fec_ini = time.strftime('%Y-%m-%d')
        fec_end = (fields.Date.from_string(str(fec_ini)) +
                   (relativedelta(months=2)))
        service_product = self.env.ref('product.product_product_consultant')
        service_product.write({'performance': 5.0,
                               'recurring_service': True})
        service_product.performance = 5.0
        service_product.route_ids = [
            (6, 0,
             [self.ref('procurement_service_project.route_serv_project')])]
        sale_vals = {
            'name': 'sale order 2',
            'partner_id': self.ref('base.res_partner_1'),
            'partner_shipping_id': self.ref('base.res_partner_1'),
            'partner_invoice_id': self.ref('base.res_partner_1'),
            'project_by_task': 'yes',
            'payer': 'school'}
        sale_line_vals = {
            'partner_id': self.ref('base.res_partner_1'),
            'product_id': service_product.id,
            'name': service_product.name,
            'product_uom_qty': 7,
            'product_uos_qty': 7,
            'product_uom': service_product.uom_id.id,
            'price_unit': service_product.list_price,
            'performance': 5.0,
            'january': True,
            'february': True,
            'week4': True,
            'week5': True,
            'tuesday': True,
            'thursday': True,
            'start_date': fec_ini,
            'start_hour': 8.00,
            'end_date': fec_end,
            'end_hour': 12.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order2 = self.sale_model.create(sale_vals)

    def test_event_planned_by_sale_line(self):
        self.sale_order2.action_button_confirm()
        self.sale_order2.project_id.recurring_next_date = (
            time.strftime('%Y-%m-%d'))
        self.account_model._cron_recurring_create_invoice()
        self.sale_order2.onchange_template_id(
            self.env.ref('website_quote.website_quote_template_1').id)
        self.sale_order2.order_line[0].onchange_product_tmpl_id()
        self.sale_order2.order_line[0].onchange_start_end_date()
        cond = [('analytic_account_id', '=', self.sale_order2.project_id.id)]
        project = self.project_model.search(cond)
        self.assertNotEqual(
            len([project]), 0, 'Analytic account not found')
        cond = [('project_id', '=', project.id)]
        event = self.event_model.search(cond, limit=1)
        self.assertNotEqual(
            len([event]), 0, 'Sale order withour event')
        self.sale_order2.order_line[0].event_id = event.id
        event._compute_event_tasks()
