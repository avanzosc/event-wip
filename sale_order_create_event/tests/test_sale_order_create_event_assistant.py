# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016-2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.event_track_assistant.tests.\
    test_event_track_assistant import TestEventTrackAssistant
from openerp import exceptions, fields
from .common import SaleOrderCreateEventSetup

str2date = fields.Date.from_string


class TestSaleOrderCreateEventAssistant(
        TestEventTrackAssistant, SaleOrderCreateEventSetup):

    def setUp(self):
        super(TestSaleOrderCreateEventAssistant, self).setUp()

    def test_event_track_registration_open_button(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEventAssistant,
              self).test_event_track_registration_open_button()
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_cancel()

    def test_event_track_assistant_delete(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEventAssistant,
              self).test_event_track_assistant_delete()

    def test_event_track_assistant_delete_from_event(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        self.event = self.event_model.search(cond, limit=1)[:1]
        super(TestSaleOrderCreateEventAssistant,
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
        super(TestSaleOrderCreateEventAssistant,
              self).test_event_assistant_track_assistant_confirm_assistant()
        self.assertNotEqual(len(self.event.work_ids), 0)
        presence = self.event.track_ids[0].presences[0]
        presence.button_canceled()
        cond = [('event_id', '=', presence.event.id),
                ('date', '=', presence.session.real_date_end),
                ('task_id', '=', presence.session.tasks[:1].id),
                ('user_id', '=', presence.partner.employee_id.user_id.id)]
        self.work_model.search(cond, limit=1)
        self.assertEqual(len(self.work_model.search(cond, limit=1)), 0,
                         'Found project task work after cancel presence')
        presence.button_completed()
        self.assertNotEqual(
            len(self.work_model.search(cond, limit=1)), 0,
            'Not project task work found after completed presence')
        presence.button_pending()
        cond = [('event_id', '=', presence.event.id),
                ('date', '=', presence.session.real_date_end),
                ('task_id', '=', presence.session.tasks[:1].id),
                ('user_id', '=', presence.partner.employee_id.user_id.id)]
        self.work_model.search(cond, limit=1)
        self.assertEqual(len(self.work_model.search(cond, limit=1)), 0,
                         'Found project task work after pending presence')
        report_vals = {'from_date': presence.session_date_without_hour,
                       'to_date': presence.session_date_without_hour}
        employee = self.ref('hr.employee_fp')
        report = self.env['wiz.actual.services.report'].create(report_vals)
        report.with_context(
            active_id=employee).show_employee_actual_services()
