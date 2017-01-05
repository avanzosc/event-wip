# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions, fields
from dateutil.relativedelta import relativedelta

datetime2str = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string


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
        self.assertTrue(self.partner.registered_partner)
        dict_add_wiz = registration.with_context().button_registration_open()
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).browse(dict_add_wiz.get('res_id'))
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('track_ids.presences')), 0)
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
        self.assertFalse(del_wiz.notes)
        with self.assertRaises(exceptions.Warning):
            del_wiz.action_delete_past_and_later()
        del_wiz.onchange_information()
        del_wiz.write({
            'removal_date': '2025-01-25',
            'notes': 'Registration canceled by system',
        })
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': '2025-01-25',
        })
        del_wiz.onchange_information()
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.action_delete_past_and_later()
        self.assertEquals(registration.state, 'cancel')
        self.assertEquals(registration.removal_date, '2025-01-25')
        self.assertEquals(registration.notes,
                          'Registration canceled by system')

    def test_event_sessions_delete_past_and_later_date(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).create({
                'partner': self.partner.id,
                'removal_date': '2025-12-01',
                'notes': 'Registration canceled by system',
            })
        from_date = del_wiz.from_date
        to_date = del_wiz.to_date
        self.assertFalse(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': '2025-01-25',
            'to_date': to_date,
        })
        del_wiz.onchange_information()
        self.assertTrue(del_wiz.message)
        self.assertTrue(del_wiz.past_sessions)
        self.assertFalse(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': '2025-01-25',
        })
        del_wiz.onchange_information()
        self.assertTrue(del_wiz.message)
        self.assertFalse(del_wiz.past_sessions)
        self.assertTrue(del_wiz.later_sessions)
        del_wiz.write({
            'from_date': from_date,
            'to_date': to_date,
        })
        del_wiz.action_delete_past_and_later()
        del_wiz.action_nodelete_past_and_later()
        registration = self.event.registration_ids[:1]
        self.assertEquals(registration.state, 'cancel')
        self.assertEquals(registration.removal_date, '2025-12-01')
        self.assertEquals(registration.notes,
                          'Registration canceled by system')

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

    def test_event_change_registration_to_another_event(self):
        registration_vals = ({'event_id': self.event.id,
                              'partner_id': self.ref('base.res_partner_25'),
                              'state': 'draft',
                              'date_start': '2025-01-20 00:00:00',
                              'date_end': '2025-01-31 00:00:00'})
        registration = self.registration_model.create(registration_vals)
        wiz_vals = {'name': 'confirm assistants'}
        wiz = self.wiz_confirm_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': self.event.ids}).action_confirm_assistant()
        cond = [('id', '!=', self.event.id)]
        new_event = self.event_model.search(cond, limit=1)
        wiz_another_vals = {
            'event_registration_id': registration.id,
            'event_id': self.event.id,
            'new_event_id': new_event.id}
        wiz = self.wiz_change_event_model.create(wiz_another_vals)
        var_fields = ['new_event_id', 'event_id']
        wiz.with_context(
            {'active_id': registration.id}).default_get(var_fields)
        wiz.with_context(
            {'active_ids': self.event.ids}).button_change_registration_event()
        presences = self.event.mapped('track_ids.presences').filtered(
            lambda x: x.partner.id == self.ref('base.res_partner_25') and
            x.state != 'canceled')
        self.assertEqual(
            len(presences), 0, 'Presences found in old event')
        new_registration = new_event.mapped('registration_ids').filtered(
            lambda x: x.partner_id.id == self.ref('base.res_partner_25'))
        self.assertNotEqual(
            len(new_registration), 0, 'Registration not found in new event')
