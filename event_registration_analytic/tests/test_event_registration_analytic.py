# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent
from openerp import fields


class TestEventRegistrationAnalytic(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestEventRegistrationAnalytic, self).setUp()
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']
        self.wiz_cancel_model =\
            self.env['wiz.event.delete.canceled.registration']
        self.wiz_impute_model = self.env['wiz.impute.in.presence.from.session']
        self.claim_model = self.env['crm.claim']
        self.registration_model = self.env['event.registration']
        self.account_model = self.env['account.analytic.account']
        self.wiz_another_model = self.env['wiz.registration.to.another.event']
        self.wiz_append_model = self.env['wiz.event.append.assistant']
        self.partner = self.env.ref('base.res_partner_address_23')
        self.partner.parent_id.bank_ids = self.env['res.partner.bank'].create({
            'acc_number': 'ES9121000418450200051332',
            'partner_id': self.partner.id,
            'state': 'iban',
            'mandate_ids': [(0, 0, {'format': 'sepa',
                                    'signature_date': fields.Date.today()})],
        })

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
            self.assertEquals(
                event.count_all_registrations,
                event.count_registrations + event.count_teacher_registrations)
            teachers = event.mapped('employee_registration_ids.partner_id')
            self.assertEquals(
                event.count_pickings,
                len(self.env['stock.picking'].search(
                    [('partner_id', 'in', teachers.ids)])))
            self.assertEquals(
                event.count_moves,
                len(self.env['stock.move'].search(
                    [('partner_id', 'in', teachers.ids)])))
            self.assertEquals(
                event.count_presences,
                len(event.mapped('track_ids.presences')))
            event.show_all_registrations()
            event.show_teacher_registrations()
            event.show_teacher_pickings()
            event.show_teacher_moves()
            result = event.show_presences()
            domain = [('id', 'in', event.mapped('track_ids.presences').ids)]
            self.assertEqual(
                result['domain'], domain, 'Error in show event presences')
            self.assertEquals(event.count_all_registrations,
                              len(event.no_employee_registration_ids) +
                              len(event.employee_registration_ids))
            self.assertEquals(event.count_registrations,
                              len(event.no_employee_registration_ids))
            self.assertEquals(event.count_teacher_registrations,
                              len(event.employee_registration_ids))
            self.assertEquals(
                event.count_registrations + event.count_teacher_registrations,
                len(event.registration_ids))
            registration_vals = ({'event_id': event.id,
                                  'partner_id': self.partner.id,
                                  'state': 'draft',
                                  'date_start': '2025-01-15 08:00:00',
                                  'date_end': '2025-02-28 09:00:00'})
            registration = self.registration_model.create(registration_vals)
            event._compute_seats()
            self.assertEqual(
                event.seats_unconfirmed, 1, 'Draft registrations error')
            wiz_vals = {'name': 'confirm assistants'}
            wiz = self.wiz_confirm_model.create(wiz_vals)
            wiz.with_context(
                {'active_ids': [event.id]}).action_confirm_assistant()
            self.assertNotEqual(
                registration.state, 'draft', 'Registration not confirmed')
            registration._calculate_required_account()
            registration._onchange_partner()
            registration.registration_open()
            self.env.ref('base.res_partner_address_23')
            self.assertEqual(
                self.partner.parent_num_bank_accounts,
                self.partner.parent_id.num_bank_accounts,
                'Student and family with different number of banks')
            self.assertEqual(
                self.partner.parent_num_valid_mandates,
                self.partner.parent_id.num_valid_mandates,
                'Student and family with different number of valid mandates')
            self.assertEqual(
                self.partner.parent_num_invoices,
                self.partner.parent_id.num_invoices,
                'Student and family with different number of invoices')
            self.wiz_impute_model.with_context(
                {'active_ids':
                 [event.track_ids[0].id]}).default_get(['lines'])
            impute_line_vals = {
                'presence': event.track_ids[0].presences[0].id,
                'session': event.track_ids[0].presences[0].session.id,
                'session_date': event.track_ids[0].presences[0].session_date,
                'partner': event.track_ids[0].presences[0].partner.id,
                'notes': 'presence notes',
                'create_claim': True}
            wiz_impute = self.wiz_impute_model.create(
                {'lines': [(0, 0, impute_line_vals)]})
            wiz_impute.button_impute_hours()
            event.track_ids._compute_real_duration()
            event.registration_ids.write({'state': 'cancel'})
            presences = event.track_ids.mapped('presences')
            presences.write({'state': 'canceled'})
            wiz_del = self.wiz_cancel_model.create({})
            wiz_del.with_context(
                {'active_ids': [event.id]}).delete_canceled_registration()
            self.assertEqual(len(event.registration_ids), 0,
                             'Event with registrations')

    def test_sale_order_create_event_by_task(self):
        self.assertEquals(self.sale_order.project_by_task, 'no')
        self.sale_order.write({'project_by_task': 'yes'})
        self.sale_order2 = self.sale_order.copy()
        self.sale_order2.project_id = self.sale_order.project_id
        self.sale_order2.action_button_confirm()
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {'partner': self.partner.id}
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
        vals = self.wiz_append_model._prepare_data_for_account_not_employee(
            events[0], events[0].registration_ids[0])
        analytic_account = self.account_model.create(vals)
        registration = events[0].registration_ids[0]
        registration.analytic_account = analytic_account
        registration._prepare_wizard_registration_open_vals()
        cond = [('id', '!=', events[0].id),
                ('sale_order', '!=', False)]
        events = self.event_model.search(cond, limit=1)
        for new_event in events:
            wiz_another_vals = {
                'event_registration_id': registration.id,
                'event_id': registration.event_id.id,
                'new_event_id': new_event.id}
            wiz = self.wiz_another_model.create(wiz_another_vals)
            var_fields = ['new_event_id', 'event_id']
            wiz.with_context(
                {'active_id': registration.id}).default_get(var_fields)
            wiz.with_context(
                {'active_ids':
                 registration.event_id.ids})._change_registration_event()

            wiz_vals = {'name': 'confirm assistants'}
            wiz = self.wiz_confirm_model.create(wiz_vals)
            wiz.with_context(
                {'active_ids': [new_event.id]}).action_confirm_assistant()

            dat = self.wiz_append_model._prepare_data_for_account_not_employee(
                new_event, registration)
            self.assertEquals(
                registration.analytic_account.name, dat.get('name', False),
                'Analytic account without new description')
            registration.write({'notes': 'Registration cancel by test'})
            registration.button_reg_cancel()
            self.assertEqual(
                registration.analytic_account.state, 'cancelled',
                'Analytic account not canceled')
