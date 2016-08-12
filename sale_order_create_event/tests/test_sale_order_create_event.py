# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import exceptions


class TestSaleOrderCreateEvent(common.TransactionCase):

    def setUp(self):
        super(TestSaleOrderCreateEvent, self).setUp()
        self.task_model = self.env['project.task']
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.event_model = self.env['event.event']
        self.procurement_model = self.env['procurement.order']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.registration_model = self.env['event.registration']
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
        })
        sale_vals = {
            'name': 'sale order 1',
            'partner_id': self.ref('base.res_partner_1'),
            'project_id': self.account.id,
            'project_by_task': 'no',
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
            'end_date': '2025-02-28',
            'end_hour': 12.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_sale_order_create_event(self):
        self.assertEquals(len(self.project.tasks), 0)
        self.sale_order.action_button_confirm()
        self.assertNotEquals(len(self.project.tasks), 0)
        self.assertEquals(
            len(self.project.tasks),
            len(self.sale_order.mapped('order_line').filtered(
                lambda l: l.product_id.recurring_service)))
        for task in self.project.tasks:
            button = task.show_sessions_from_task()
            self.assertEquals(button.get('type'), 'ir.actions.act_window')
            self.assertEquals(button.get('res_model'), 'event.track')
            task.button_recalculate_sessions()
            self.assertNotEquals(
                len(task.sessions), 0, 'Sessions no generated')
            self.assertEquals(
                len(task.sessions), task.num_sessions)
        cond = [('project_id', '=', self.project.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        wiz_vals = {
            'partner': self.ref('base.res_partner_26'),
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=event.ids).create(wiz_vals)
        wiz.action_append()
        self.assertNotEqual(
            len([event]), 0, 'Sale order without event')
        self.assertEquals(
            event.my_task_ids,
            self.task_model.search([('event_id', '=', event.id)]))
        self.assertEquals(len(event.my_task_ids), event.count_tasks)

    def test_sale_order_create_event_by_task(self):
        self.sale_order.write({
            'project_by_task': 'yes',
        })
        self.sale_order.action_button_confirm()
        cond = [('project_id', '=', self.project.id)]
        event = self.event_model.search(cond, limit=1)
        wiz_vals = {
            'partner': self.ref('base.res_partner_26'),
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=event.ids).create(wiz_vals)
        wiz.action_append()
        self.assertNotEqual(
            len([event]), 0, 'Sale order without event')
        self.assertEquals(
            event.my_task_ids,
            self.task_model.search([('event_id', '=', event.id)]))
        self.assertEquals(len(event.my_task_ids), event.count_tasks)
        self.sale_order.action_cancel()
        self.assertEquals(self.sale_order.state, 'cancel')

    def test_sale_order_confirm(self):
        self.assertEquals(self.sale_order.state, 'draft')
        self.sale_order.project_id = False
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_button_confirm()
        self.service_product.recurring_service = False
        self.sale_order.action_button_confirm()
        self.assertNotEquals(self.sale_order.state, 'draft')

    def test_onchange_line_times(self):
        for line in self.sale_order.order_line:
            line.start_hour = 10
            line.end_hour = 12
            performance = line.end_hour - line.start_hour
            line.onchange_date_begin()
            self.assertEquals(line.performance, performance)
