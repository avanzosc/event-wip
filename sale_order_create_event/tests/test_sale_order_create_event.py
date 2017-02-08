# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016-2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.event_track_assistant.tests.\
    test_event_track_assistant import TestEventTrackAssistant
from openerp import exceptions, fields

str2date = fields.Date.from_string


class TestSaleOrderCreateEvent(TestEventTrackAssistant):

    def setUp(self):
        super(TestSaleOrderCreateEvent, self).setUp()
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
            'end_hour': 09.00}
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

    def test_sale_order_create_event_by_task(self):
        self.sale_order.write({
            'project_by_task': 'yes',
        })
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

    def test_change_session_date(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        wiz_vals = {'days': 35}
        wiz = self.change_date_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': [event.track_ids[len(
                event.track_ids)-1].id]}).change_session_date()
        self.assertEqual(
            str2date(event.track_ids[len(
                event.track_ids)-1].date), str2date(event.date_end),
            'Session and event with different end date')
        wiz_vals = {'days': -28}
        wiz = self.change_date_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': [event.track_ids[0].id]}).change_session_date()
        self.assertEqual(
            str2date(event.track_ids[0].date), str2date(event.date_begin),
            'Session and event with different start date')

    def test_event_track_registration_open_button(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEvent,
              self).test_event_track_registration_open_button()
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_cancel()

    def test_event_track_assistant_delete(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEvent,
              self).test_event_track_assistant_delete()

    def test_event_track_assistant_delete_from_event(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEvent,
              self).test_event_track_assistant_delete_from_event()

    def test_event_assistant_track_assistant_confirm_assistant(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        contract = self.contract_model.create({
            'name': u'Contract {}'.format(self.partner.name),
            'employee_id': self.ref('hr.employee_fp'),
            'partner': self.partner.id,
            'type_id': self.ref('hr_contract.hr_contract_type_emp'),
            'wage': 500,
            'date_start': self.event.date_begin,
            'working_hours': self.ref('resource.timesheet_group1'),
        })
        workable_wiz = self.wiz_workable_model.with_context(
            active_id=contract.id).create({})
        workable_wiz.button_calculate_workables_and_festives()
        super(TestSaleOrderCreateEvent,
              self).test_event_assistant_track_assistant_confirm_assistant()
        self.assertNotEqual(len(self.event.work_ids), 0)

    def test_duplicate_sale_order(self):
        self.sale_order.project_by_task = 'yes'
        self.sale_order.action_button_confirm()
        self.assertTrue(self.sale_order.mapped('order_line.event_id'))
        copy_sale_order = self.sale_order.copy()
        self.assertEquals(copy_sale_order.state, 'draft')
        self.assertFalse(copy_sale_order.mapped('order_line.event_id'))
