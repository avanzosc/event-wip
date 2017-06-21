# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields
from dateutil.relativedelta import relativedelta
from .common import EventTrackAssistantSetup

datetime2str = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string
date2str = fields.Date.to_string


class TestEventTrackAssistantOnly(EventTrackAssistantSetup):

    def setUp(self):
        super(TestEventTrackAssistantOnly, self).setUp()

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

    def test_count_absences_create_claim(self):
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({'partner': self.partner.id})
        add_wiz.action_append()
        presences = self.event.mapped('track_ids.presences')
        presences.write({'state': 'absent'})
        max_presence = max(presences, key=lambda x: x.id)
        max_presence.count_absences_create_claim()
        categ_id = self.ref('event_track_assistant.crm_case_categ_possible_'
                            'low')
        cond = [('event_id', '=', max_presence.event.id),
                ('session_id', '=', max_presence.session.id),
                ('categ_id', '=', categ_id)]
        self.assertEqual(
            len(self.claim_model.search(cond, limit=1)), 1,
            'Claim not found for 3 absences.')

    def test_change_session_duration(self):
        wiz = self.wiz_duration_model.create({'new_duration': 5})
        wiz.with_context(
            active_ids=self.event.track_ids[0].ids).change_session_duration()
        self.assertEqual(
            self.event.track_ids[0].duration, 5,
            'Bad change session duration')
