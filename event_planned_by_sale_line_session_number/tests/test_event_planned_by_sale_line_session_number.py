# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class EventPlannedBySaleLineSessionNumber(common.TransactionCase):

    def setUp(self):
        super(EventPlannedBySaleLineSessionNumber, self).setUp()
        self.task_model = self.env['project.task']
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.procurement_model = self.env['procurement.order']
        self.impute_model = self.env['wiz.impute.in.presence.from.session']
        self.line_model = self.env['wiz.impute.in.presence.from.session.line']
        self.contract_model = self.env['hr.contract']
        self.wiz_workable_model = self.env['wiz.calculate.workable.festive']
        self.change_date_model = self.env['wiz.change.session.date']
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2025-01-15',
                        'date': '2025-02-28',
                        'use_tasks': True}
        self.account = self.account_model.create(account_vals)
        self.project = self.env['project.project'].search(
            [('analytic_account_id', '=', self.account.id)], limit=1)[:1]
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        self.service_product.write({
            'performance': 5.0,
            'recurring_service': True,
            'route_ids':
            [(6, 0,
              [self.ref('procurement_service_project.route_serv_project')])],
            'ticket_event_product_ids':
            [(6, 0,
              [self.ref('event_sale.product_product_event')])],
        })
        sale_vals = {
            'name': 'sale order 1200',
            'partner_id': self.ref('base.res_partner_1'),
            'project_id': self.account.id,
            'project_by_task': 'yes',
        }
        sale_line_vals = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price,
            'performance': self.service_product.performance,
            'january': True,
            'february': True,
            'week4': True,
            'week5': True,
            'tuesday': True,
            'thursday': True,
            'start_date': '2025-01-15',
            'start_hour': 8.00,
            'session_number': 4,
            'end_hour': 09.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_event_planned_by_sale_line_session_number(self):
        self.sale_order._generate_lines_end_date(self.sale_order.order_line[0])
        self.assertEquals(self.sale_order.order_line[0].end_date,
                          '2025-01-30', 'Bad date end of sale line')
