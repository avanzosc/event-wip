# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions, fields
from dateutil.relativedelta import relativedelta

datetime2str = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string
date2str = fields.Date.to_string


class TestEventTrackAssistant(common.TransactionCase):

    def setUp(self):
        super(TestEventTrackAssistant, self).setUp()
        self.env.user.write({
            'tz': u'UTC',
        })
        self.event_model = self.env['event.event']
        self.presence_model = self.env['event.track.presence']
        self.registration_model = self.env['event.registration']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.wiz_del_model = self.env['wiz.event.delete.assistant']
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']
        self.wiz_impute_model = self.env['wiz.impute.in.presence.from.session']
        self.wiz_change_event_model =\
            self.env['wiz.registration.to.another.event']
        self.claim_model = self.env['crm.claim']
        self.partner_model = self.env['res.partner']
        self.config_model = self.env['marketing.config.settings']
        self.parent = self.partner_model.create({
            'name': 'Parent Partner',
        })
        self.partner = self.partner_model.create({
            'name': 'Test Partner',
        })
        event_vals = {
            'name': 'Registration partner test',
            'date_begin': '2025-01-20',
            'date_end': '2025-01-30',
            'track_ids': [(0, 0, {'name': 'Session 1',
                                  'date': '2025-01-22 00:00:00'}),
                          (0, 0, {'name': 'Session 2',
                                  'date': '2025-01-25 00:00:00'}),
                          (0, 0, {'name': 'Session 3',
                                  'date': '2025-01-28 00:00:00'})]
        }
        self.event = self.event_model.create(event_vals)

    def test_event_track_registration_open_button(self):
        self.assertEquals(len(self.event.mapped('track_ids.presences')), 0)
        self.assertFalse(self.partner.registered_partner)
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
        }
        registration = self.registration_model.create(registration_vals)
        registration._onchange_partner()
        self.assertTrue(self.partner.registered_partner)
        dict_add_wiz = registration.with_context().button_registration_open()
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).browse(dict_add_wiz.get('res_id'))
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('track_ids.presences')), 0)
        configs = self.config_model.search([])
        configs.write({'show_all_customers_in_presences': True})
        presence = self.event.track_ids[0].presences[0]
        presence._compute_allowed_partner_ids()
        configs.write({'show_all_customers_in_presences': False})
        registration.date_start = str2datetime(self.event.date_begin) -\
            relativedelta(days=1)
        self.assertNotEquals(registration.date_start, self.event.date_begin)
        res = registration._onchange_date_start()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_start, self.event.date_begin)
        registration.date_end = str2datetime(self.event.date_end) +\
            relativedelta(days=1)
        self.assertNotEquals(registration.date_end, self.event.date_end)
        res = registration._onchange_date_end()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_end, self.event.date_end)
        registration.write({
            'date_start': str2datetime(self.event.date_begin) +
            relativedelta(days=1),
            'date_end': str2datetime(self.event.date_begin) -
            relativedelta(days=1),
        })
        self.assertNotEquals(registration.date_end, self.event.date_end)
        res = registration._onchange_date_end()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_end, self.event.date_end)
        registration.write({
            'date_start': str2datetime(self.event.date_end) +
            relativedelta(days=1),
            'date_end': str2datetime(self.event.date_end) -
            relativedelta(days=1),
        })
        self.assertNotEquals(registration.date_start, self.event.date_begin)
        res = registration._onchange_date_start()
        self.assertTrue(res.get('warning'))
        self.assertEquals(registration.date_start, self.event.date_begin)

    def test_event_track_assistant_delete(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        self.assertEquals(self.partner.session_count, 0)
        self.assertEquals(self.partner.presences_count, 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        self.partner.invalidate_cache()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        self.assertNotEquals(self.partner.session_count, 0)
        self.assertNotEquals(self.partner.presences_count, 0)
        self.assertIn(
            self.partner.id,
            self.event.mapped('registration_ids.partner_id').ids,
            'Partner should be registered')
        show_sessions = self.partner.show_sessions_from_partner()
        self.assertEquals(
            show_sessions.get('res_model'), 'event.track')
        show_presences = self.partner.show_presences_from_partner()
        self.assertEquals(
            show_presences.get('res_model'), 'event.track.presence')
        presences = self.event.mapped('track_ids.presences')
        self.assertNotEquals(len(presences), 0)
        new_presence = self.presence_model.new({
            'session': self.event.track_ids[:1].id,
        })
        self.assertEquals(new_presence.event, self.event)
        self.assertIn(self.partner, new_presence.allowed_partner_ids)
        registration = self.event.registration_ids[:1]
        dict_del_wiz = registration.new_button_reg_cancel()
        self.assertNotEquals(registration.state, 'cancel')
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).browse(dict_del_wiz.get('res_id'))
        from_date = del_wiz.from_date
        to_date = del_wiz.to_date
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': to_date,
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        with self.assertRaises(exceptions.Warning):
            del_wiz.action_delete()
        del_wiz.write({
            'notes': 'Registration canceled by test',
        })
        del_wiz.action_delete()
        self.assertEquals(registration.state, 'cancel')

    def test_event_track_assistant_delete_from_event(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        self.assertFalse(del_wiz.registration)
        from_date = del_wiz.from_date
        to_date = del_wiz.to_date
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': to_date,
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': '2025-01-25',
        })
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        with self.assertRaises(exceptions.Warning):
            del_wiz.action_delete()
        del_wiz.write({
            'notes': 'Registration canceled by test',
        })
        del_wiz.action_delete()
        registration = self.event.registration_ids.filtered(
            lambda r: r.partner_id == self.partner)
        self.assertEquals(registration.state, 'cancel')

    def test_event_assistant_add_wizard(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        from_date = add_wiz.from_date
        to_date = add_wiz.to_date
        min_from_date = date2str(str2datetime(add_wiz.min_from_date).date())
        max_to_date = date2str(str2datetime(add_wiz.max_to_date).date())
        wrong_from_date = str2datetime(add_wiz.min_from_date) -\
            relativedelta(days=1)
        wrong_to_date = str2datetime(add_wiz.max_to_date) +\
            relativedelta(days=1)
        not_warn = add_wiz.onchange_dates_and_partner()
        self.assertNotIn('warning', not_warn)
        add_wiz.write({
            'from_date': to_date,
            'to_date': from_date,
        })
        warn1 = add_wiz.onchange_dates_and_partner()
        self.assertIn('warning', warn1)
        self.assertEquals(add_wiz.from_date, min_from_date)
        self.assertEquals(add_wiz.to_date, max_to_date)
        add_wiz.write({
            'from_date': wrong_from_date,
            'to_date': to_date,
        })
        warn2 = add_wiz.onchange_dates_and_partner()
        self.assertIn('warning', warn2)
        self.assertEquals(add_wiz.from_date, min_from_date)
        self.assertEquals(add_wiz.to_date, max_to_date)
        add_wiz.write({
            'from_date': from_date,
            'to_date': wrong_to_date,
        })
        warn3 = add_wiz.onchange_dates_and_partner()
        self.assertIn('warning', warn3)
        self.assertEquals(add_wiz.from_date, min_from_date)
        self.assertEquals(add_wiz.to_date, max_to_date)
        add_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        warn4 = add_wiz.onchange_dates_and_partner()
        self.assertIn('warning', warn4)
        self.assertEquals(add_wiz.from_date, min_from_date)
        self.assertEquals(add_wiz.to_date, max_to_date)

    def test_event_assistant_delete_wizard(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        from_date = self.event.track_ids[:1].date
        to_date = self.event.track_ids[-1:].date
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id,
                                               'from_date': from_date,
                                               'to_date': to_date})
        min_from_date = date2str(str2datetime(del_wiz.min_from_date).date())
        max_to_date = date2str(str2datetime(del_wiz.max_to_date).date())
        wrong_from_date = str2datetime(del_wiz.min_from_date) -\
            relativedelta(days=2)
        wrong_to_date = str2datetime(del_wiz.max_to_date) +\
            relativedelta(days=2)
        not_warn = del_wiz.onchange_dates()
        self.assertNotIn('warning', not_warn)
        self.assertNotEquals(del_wiz.from_date, min_from_date)
        self.assertNotEquals(del_wiz.to_date, max_to_date)
        del_wiz.write({
            'from_date': to_date,
            'to_date': from_date,
        })
        warn1 = del_wiz.onchange_dates()
        self.assertIn('warning', warn1)
        self.assertEquals(del_wiz.from_date, min_from_date)
        self.assertEquals(del_wiz.to_date, max_to_date)
        del_wiz.write({
            'from_date': wrong_from_date,
            'to_date': to_date,
        })
        warn2 = del_wiz.onchange_dates()
        self.assertIn('warning', warn2)
        self.assertEquals(del_wiz.from_date, min_from_date)
        self.assertEquals(del_wiz.to_date, max_to_date)
        del_wiz.write({
            'from_date': from_date,
            'to_date': wrong_to_date,
        })
        warn3 = del_wiz.onchange_dates()
        self.assertIn('warning', warn3)
        self.assertEquals(del_wiz.from_date, min_from_date)
        self.assertEquals(del_wiz.to_date, max_to_date)

    def test_event_assistant_track_assistant_confirm_assistant(self):
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        registration = self.event.registration_ids[:1]
        wiz_vals = {'name': 'confirm assistants'}
        wiz = self.wiz_confirm_model.create(wiz_vals)
        wiz.with_context(
            active_ids=self.event.ids).action_confirm_assistant()
        self.assertNotEqual(
            registration.state, 'draft',
            'Registration should have been confirmed.')
        wiz_impute = self.wiz_impute_model.with_context(
            active_ids=self.event.track_ids.ids).create({})
        self.assertNotEquals(len(wiz_impute.lines), 0)
        wiz_impute.lines.write({
            'create_claim': True,
        })
        with self.assertRaises(exceptions.Warning):
            wiz_impute.button_impute_hours()
        wiz_impute.lines.write({
            'notes': 'Created claim from event.track.presence',
        })
        self.assertEquals(len(self.event.claim_ids), 0)
        self.assertEquals(self.event.claim_count, 0)
        wiz_impute.button_impute_hours()
        self.assertNotEqual(len(self.event.claim_ids), 0)
        self.assertNotEqual(self.event.claim_count, 0)
        for track in self.event.track_ids:
            self.assertNotEqual(len(track.claim_ids), 0)
            self.assertNotEqual(track.claim_count, 0)

    def test_event_change_registration_to_another_event(self):
        self.assertFalse(
            self.event.mapped('track_ids.presences').filtered(
                lambda x: x.partner == self.partner))
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
            'state': 'draft',
            'date_start': '2025-01-20 00:00:00',
            'date_end': '2025-01-31 00:00:00',
        }
        registration = self.registration_model.create(registration_vals)
        self.assertEquals(registration.state, 'draft')
        wiz_vals = {'name': 'confirm assistants'}
        wiz = self.wiz_confirm_model.with_context(
            active_ids=self.event.ids).create(wiz_vals)
        wiz.action_confirm_assistant()
        self.assertEquals(registration.state, 'open')
        partner_presences = self.event.mapped('track_ids.presences').filtered(
            lambda x: x.partner == self.partner)
        self.assertTrue(
            partner_presences.filtered(lambda p: p.state != 'canceled'))
        self.assertFalse(
            partner_presences.filtered(lambda p: p.state == 'canceled'))
        new_event = self.event.copy()
        wiz_another_vals = {
            'new_event_id': new_event.id,
        }
        change_wiz = self.wiz_change_event_model.with_context(
            active_id=registration.id).create(wiz_another_vals)
        self.assertEquals(change_wiz.event_id, registration.event_id)
        self.assertEquals(change_wiz.event_registration_id, registration)
        change_wiz.button_change_registration_event()
        self.assertNotEquals(self.event, registration.event_id)
        self.assertEquals(new_event, registration.event_id)
        self.assertEquals(registration.state, 'draft')
        partner_presences = self.event.mapped('track_ids.presences').filtered(
            lambda x: x.partner == self.partner)
        self.assertFalse(
            partner_presences.filtered(lambda p: p.state != 'canceled'))
        self.assertTrue(
            partner_presences.filtered(lambda p: p.state == 'canceled'))
        new_registration = new_event.mapped('registration_ids').filtered(
            lambda x: x.partner_id == self.partner)
        self.assertNotEqual(
            len(new_registration), 0, 'Registration not found in new event')

    def test_update_registration_dates_from_wizard(self):
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
            'date_start': '2025-01-20',
            'date_end': '2025-01-30'}
        registration = self.registration_model.create(registration_vals)
        wiz_vals = {'partner': self.partner.id,
                    'from_date': '2025-01-22',
                    'to_date': '2025-01-28'}
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create(wiz_vals)
        add_wiz._update_registration_start_date(registration)
        self.assertEquals(registration.date_start, '2025-01-22 00:00:00')
        add_wiz._update_registration_date_end(registration)
        self.assertEquals(registration.date_end, '2025-01-28 00:00:00')
