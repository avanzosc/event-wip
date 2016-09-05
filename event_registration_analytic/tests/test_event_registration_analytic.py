# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestEventRegistrationAnalytic(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestEventRegistrationAnalytic, self).setUp()
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']

    def test_sale_order_create_event(self):
        self.assertEquals(self.sale_order.project_by_task, 'no')
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {'partner': self.ref('base.res_partner_26')}
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        wiz.action_append()
        for event in events:
            self.assertEquals(event.count_registrations,
                              len(event.no_employee_registration_ids))
            self.assertEquals(event.count_teacher_registrations,
                              len(event.employee_registration_ids))
            self.assertEquals(
                event.count_registrations + event.count_teacher_registrations,
                len(event.registration_ids))
            registration_vals = ({'event_id': event.id,
                                  'partner_id':
                                  self.env.ref('base.res_partner_25').id,
                                  'state': 'draft',
                                  'date_start': '2025-01-15 08:00:00',
                                  'date_end': '2025-02-28 09:00:00'})
            registration = self.registration_model.create(registration_vals)
            wiz_vals = {'name': 'confirm assistants'}
            wiz = self.wiz_confirm_model.create(wiz_vals)
            wiz.with_context(
                {'active_ids': [event.id]}).action_confirm_assistant()
            self.assertNotEqual(
                registration.state, 'draft', 'Registration not confirmed')

    def test_sale_order_create_event_by_task(self):
        self.assertEquals(self.sale_order.project_by_task, 'no')
        self.sale_order.write({'project_by_task': 'yes'})
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {'partner': self.ref('base.res_partner_26')}
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        wiz.action_append()
        for event in events:
            self.assertEquals(event.count_registrations,
                              len(event.no_employee_registration_ids))
            self.assertEquals(event.count_teacher_registrations,
                              len(event.employee_registration_ids))
            self.assertEquals(
                event.count_registrations + event.count_teacher_registrations,
                len(event.registration_ids))
