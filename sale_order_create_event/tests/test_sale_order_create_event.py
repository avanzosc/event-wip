# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016-2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import exceptions, fields
from .common import SaleOrderCreateEventSetup

str2date = fields.Date.from_string


class TestSaleOrderCreateEvent(SaleOrderCreateEventSetup):

    def setUp(self):
        super(TestSaleOrderCreateEvent, self).setUp()

    def test_sale_order_create_event(self):
        self.assertEquals(len(self.project.tasks), 0)
        vals = {'name': 'Resource calendar for test',
                'attendance_ids':
                [(0, 0, {'name': 'a',
                         'dayofweek': '1',
                         'hour_from': 8.00,
                         'hour_to': 10.00,
                         'date_from': self.sale_order.project_id.date_start})]}
        resource = self.env['resource.calendar'].create(vals)
        self.sale_order.project_id.working_hours = resource.id
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        sessions = event.mapped('track_ids').filtered(
            lambda x: x.day == '1')
        min_session = min(sessions, key=lambda x: x.date)
        self.assertEquals(min_session.date, '2025-01-21 08:00:00',
                          'Bad date from working_hours')
        self.assertEquals(min_session.duration, 2.0,
                          'Bad duration from working_hours')
        resource.attendance_ids[0].hour_from = 7.00
        wiz = self.env['wiz.recalculate.hour.from.contract'].create({})
        account = self.sale_order.project_id
        wiz.with_context(
            active_ids=[account.id]).recalculate_session_date()
        sessions = event.mapped('track_ids').filtered(
            lambda x: x.day == '1')
        min_session = min(sessions, key=lambda x: x.date)
        self.assertEquals(min_session.date, '2025-01-21 07:00:00',
                          'Bad date from working_hours 2')
        self.assertEquals(min_session.duration, 3.0,
                          'Bad duration from working_hours 2')
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
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        self.assertTrue(event, 'Sale order without event')
        self.assertTrue(event.event_ticket_ids)
        self.assertTrue(event.my_task_ids)
        self.assertEquals(
            event.my_task_ids,
            self.task_model.search([('event_id', '=', event.id)]))
        self.assertEquals(len(event.my_task_ids), event.count_tasks)
        self.sale_order.action_cancel()
        self.assertEquals(self.sale_order.state, 'cancel')
        self.assertEquals(
            len(resource.attendance_historical_ids), 1,
            'Bad resource historical(1)')
        resource.attendance_ids[0].hour_to = 11.0
        self.assertEquals(
            len(resource.attendance_historical_ids), 2,
            'Bad resource historical(2)')

    def test_sale_order_create_event_by_task(self):
        self.sale_order.write({
            'project_by_task': 'yes',
        })
        self.sale_order.action_button_confirm()
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_button_confirm()
        self.assertEquals(len(self.project.tasks), 0)
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        self.assertTrue(event, 'Sale order without event')
        self.assertTrue(event.event_ticket_ids)
        self.assertEquals(
            event.my_task_ids,
            self.task_model.search([('event_id', '=', event.id)]))
        self.assertEquals(len(event.my_task_ids), event.count_tasks)
        with self.assertRaises(exceptions.Warning):
            event.unlink()

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

    def test_sale_order_create_event_project_address(self):
        self.sale_order.action_button_confirm()
        task = self.task_model.search([('event_id', '!=', False)], limit=1)
        if not task.event_id.address_id.street:
            task.event_id.address_id.street = 'Test address'
        task._compute_event_address()
        self.assertIn(task.event_id.address_id.street, task.event_address,
                      'Event address not found in task')
        task.project_id.partner_id = task.event_id.address_id.id
        task._compute_customer_address()
        self.assertIn(task.project_id.partner_id.street, task.customer_address,
                      'Project customer address not found in task')
