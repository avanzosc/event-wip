# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import exceptions, fields
from .._common import\
    _convert_to_local_date, _convert_to_utc_date, _convert_time_to_float
from dateutil.relativedelta import relativedelta

datetime2str = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string


class TestEventTrackAssistantDaynight(common.TransactionCase):

    def setUp(self):
        super(TestEventTrackAssistantDaynight, self).setUp()
        self.env.user.write({
            'tz': u'UTC',
        })
        self.event_model = self.env['event.event']
        self.track_model = self.env['event.track']
        self.presence_model = self.env['event.track.presence']
        self.wiz_change_hour_model = self.env['wiz.change.session.hour']
        self.datetime_now = str2datetime(fields.Datetime.now())
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

    def test_date_convert_local_method(self):
        local_date = _convert_to_local_date(self.datetime_now, tz=u'UTC')
        self.assertEquals(self.datetime_now, local_date)

    def test_date_convert_utc_method(self):
        now = self.datetime_now.replace(minute=0, second=0)
        utc_time = _convert_time_to_float(now, tz=u'UTC')
        self.assertEquals(now.hour, int(utc_time))
        utc_date = _convert_to_utc_date(now.date(), time=utc_time, tz=u'UTC')
        self.assertEquals(now, utc_date)

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

    def test_event_track_assistant_change_session_hour(self):
        track = self.event.track_ids[0]
        new_hour = 10.0
        track_date = _convert_to_local_date(track.date, self.env.user.tz)
        new_date = _convert_to_utc_date(track_date, new_hour, self.env.user.tz)
        wiz = self.wiz_change_hour_model.with_context(
            active_ids=track.ids).create({'new_hour': new_hour})
        wiz.change_session_hour()
        self.assertEquals(track.date, datetime2str(new_date))
