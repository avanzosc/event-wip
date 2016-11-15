# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions, fields
from .._common import _convert_to_local_date, _convert_to_utc_date
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
        self.track_model = self.env['event.track']
        self.presence_model = self.env['event.track.presence']
        self.registration_model = self.env['event.registration']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.wiz_del_model = self.env['wiz.event.delete.assistant']
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']
        self.wiz_change_hour_model = self.env['wiz.change.session.hour']
        self.wiz_impute_model = self.env['wiz.impute.in.presence.from.session']
        self.wiz_another_model = self.env['wiz.registration.to.another.event']
        self.claim_model = self.env['crm.claim']
        self.partner_model = self.env['res.partner']
        self.datetime_now = str2datetime(fields.Datetime.now())
        self.parent = self.partner_model.create({
            'name': 'Parent Partner',
        })
        self.partner = self.partner_model.create({
            'name': 'Test Partner',
        })
        company_model = self.env['res.company']
        company_id = company_model._company_default_get('event.track.presence')
        self.company = company_model.browse(company_id)
        self.company.write({
            'daytime_start_hour': 6.0,
            'nighttime_start_hour': 22.0,
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

    def test_date_convert_method(self):
        local_date = _convert_to_local_date(self.datetime_now, tz=u'UTC')
        self.assertEquals(self.datetime_now, local_date)

    def test_company_daytime_nighttime_hours(self):
        self.assertEquals(self.company.daytime_start_hour, 6.0)
        self.assertEquals(self.company.nighttime_start_hour, 22.0)
        with self.assertRaises(exceptions.ValidationError):
            self.company.write({
                'daytime_start_hour': -1.0,
            })
        with self.assertRaises(exceptions.ValidationError):
            self.company.write({
                'nighttime_start_hour': 25.0,
            })
        with self.assertRaises(exceptions.ValidationError):
            self.company.write({
                'daytime_start_hour': 16.0,
                'nighttime_start_hour': 10.0,
            })
        with self.assertRaises(exceptions.ValidationError):
            self.company.write({
                'daytime_start_hour': 15.0,
                'nighttime_start_hour': 15.0,
            })

    def test_assistant_event_onchange_dates(self):
        self.event.date_begin = self.event.track_ids[1].date
        res = self.event.onchange_date_begin()
        self.assertTrue(res.get('warning'))
        self.assertNotEquals(
            self.event.date_begin, self.event.track_ids[1].date)
        self.assertEquals(self.event.date_begin, self.event.track_ids[0].date)
        self.event.date_end = self.event.track_ids[1].date
        res = self.event.onchange_date_end()
        self.assertTrue(res.get('warning'))
        self.assertNotEquals(
            self.event.date_end, self.event.track_ids[1].date)
        self.assertEquals(self.event.date_end, self.event.track_ids[2].date)

    def test_assistant_event_track_dates(self):
        with self.assertRaises(exceptions.ValidationError):
            self.track_model.create({
                'event_id': self.event.id,
                'name': 'Date before',
                'date': '2025-01-19',
            })
        with self.assertRaises(exceptions.ValidationError):
            self.track_model.create({
                'event_id': self.event.id,
                'name': 'Date after',
                'date': '2025-01-31',
            })

    def test_event_track_daynight_hours_error(self):
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = start_date
        self.assertTrue(start_date == end_date)
        with self.assertRaises(exceptions.ValidationError):
            daytime, nighttime = self.presence_model._get_nightlight_hours(
                start_date, end_date)
        end_date = start_date.replace(hour=3, minute=0, second=0)
        self.assertTrue(start_date > end_date)
        with self.assertRaises(exceptions.ValidationError):
            daytime, nighttime = self.presence_model._get_nightlight_hours(
                start_date, end_date)

    def test_event_track_daynight_hours_same_day1(self):
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = self.datetime_now.replace(hour=5, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_same_day2(self):
        start_date = self.datetime_now.replace(hour=7, minute=0, second=0)
        end_date = self.datetime_now.replace(hour=21, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_same_day3(self):
        start_date = self.datetime_now.replace(hour=22, minute=30, second=0)
        end_date = self.datetime_now.replace(hour=23, minute=30, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_same_day4(self):
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = self.datetime_now.replace(hour=23, minute=30, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_same_day5(self):
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = self.datetime_now.replace(hour=21, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_same_day6(self):
        start_date = self.datetime_now.replace(hour=7, minute=30, second=0)
        end_date = self.datetime_now.replace(hour=23, minute=30, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day1(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = tomorrow.replace(hour=5, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day2(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=7, minute=0, second=0)
        end_date = tomorrow.replace(hour=21, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day3(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=22, minute=30, second=0)
        end_date = tomorrow.replace(hour=23, minute=30, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day4(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = tomorrow.replace(hour=23, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day5(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=4, minute=0, second=0)
        end_date = tomorrow.replace(hour=21, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_daynight_hours_diff_day6(self):
        tomorrow = self.datetime_now + relativedelta(days=1)
        start_date = self.datetime_now.replace(hour=7, minute=0, second=0)
        end_date = tomorrow.replace(hour=23, minute=0, second=0)
        daytime, nighttime = self.presence_model._get_nightlight_hours(
            start_date, end_date)
        diff = end_date - start_date
        difftime = (diff.days * 24) + (float(diff.seconds) / 3600)
        self.assertEquals(difftime, (daytime + nighttime))

    def test_event_track_registration_open_button(self):
        self.assertEquals(len(self.event.mapped('track_ids.presences')), 0)
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
        }
        registration = self.registration_model.create(registration_vals)
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
            active_ids=self.event.ids).create({
                'partner': self.partner.id,
            })
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
        del_wiz.action_delete()
        self.assertEquals(registration.state, 'cancel')

    def test_event_sessions_delete_past_and_later_date(self):
        self.assertEquals(len(self.event.mapped('registration_ids')), 0)
        add_wiz = self.wiz_add_model.with_context(
            active_ids=self.event.ids).create({
                'partner': self.partner.id,
            })
        add_wiz.action_append()
        self.assertNotEquals(len(self.event.mapped('registration_ids')), 0)
        del_wiz = self.wiz_del_model.with_context(
            active_ids=self.event.ids).create({
                'partner': self.partner.id,
            })
        del_wiz.action_delete_past_and_later()
        del_wiz.action_nodelete_past_and_later()

    def test_event_track_assistant_change_session_hour(self):
        track = self.event.track_ids[0]
        new_hour = 10.0
        track_date = _convert_to_local_date(track.date, self.env.user.tz)
        new_date = _convert_to_utc_date(track_date, new_hour, self.env.user.tz)
        wiz = self.wiz_change_hour_model.with_context(
            active_ids=track.ids).create({
                'new_hour': new_hour,
            })
        wiz.change_session_hour()
        self.assertEquals(track.date, datetime2str(new_date))

    def test_event_assistant_track_assistant_confirm_assistant(self):
        event_domain = [('event_id', '=', self.event.id)]
        claim = self.claim_model.search(event_domain, limit=1)
        self.assertEquals(
            len(claim), 0, 'There are not claims for the event.')
        track = self.event.track_ids[0]
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
        self.assertNotEqual(
            registration.state, 'draft',
            'Registration should have been confirmed.')
        wiz_impute = self.wiz_impute_model.with_context(
            {'active_ids': track.ids}).create({})
        self.assertNotEquals(len(wiz_impute.lines), 0)
        wiz_impute.lines.write({
            'notes': False,
            'create_claim': True,
        })
        with self.assertRaises(exceptions.Warning):
            wiz_impute.button_impute_hours()
        wiz_impute.lines.write({
            'notes': 'Created claim from event.track.presence',
        })
        wiz_impute.button_impute_hours()
        claim = self.claim_model.search(event_domain, limit=1)
        self.assertNotEqual(
            len(claim), 0, 'Created claim from presence, not found')

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
        wiz = self.wiz_another_model.create(wiz_another_vals)
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
