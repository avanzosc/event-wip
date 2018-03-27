# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta
from openerp import exceptions


class TestHrContractFinalizedEvent(common.TransactionCase):

    def setUp(self):
        super(TestHrContractFinalizedEvent, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Partner for test crm claim event presence',
            'is_company': True})
        self.employee = self.browse_ref('hr.employee_al')
        self.employee.address_home_id = self.partner.id
        contract_vals = {'name': 'New contract for employee',
                         'employee_id': self.employee.id,
                         'wage': 1000,
                         'date_start': '2018-01-01',
                         'partner': self.partner.id}
        self.contract = self.env['hr.contract'].create(contract_vals)
        today = fields.Date.today()
        date_end = '{} 12:00:00'.format(today)
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=4))
        date_begin = '{} 10:00:00'.format(date_begin)
        tracks = []
        days = []
        contador = 0
        while contador < 5:
            track = {'name': date_begin,
                     'date': date_begin,
                     'duration': 2,
                     'presences': [(0, 0, {'partner': self.partner.id,
                                           'name': self.partner.name,
                                           'session_duration': 2,
                                           'session_date': date_begin,
                                           'session_date_without_hour':
                                           date_begin,
                                           'contract': self.contract.id,
                                           'employee': self.employee.id,
                                           'employee_id': self.employee.id})]}
            tracks.append((0, 0, track))
            day = {
                'partner': self.partner.id,
                'name': self.partner.name,
                'date': date_begin[0:10]}
            days.append((0, 0, day))
            date_begin = fields.Date.to_string(fields.Date.from_string(
                date_begin) + relativedelta(days=1))
            date_begin = '{} 10:00:00'.format(date_begin)
            contador += 1
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=4))
        date_end = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=10))
        registration_vals = {
            'partner_id': self.partner.id,
            'name': self.partner.name,
            'contract': self.contract.id,
            'date_start': date_begin,
            'date_end': date_end}
        event_vals = {'name': 'Test crm claim event presence',
                      'date_begin': date_begin,
                      'date_end': date_end,
                      'registration_ids': [(0, 0, registration_vals)],
                      'track_ids': tracks}
        self.event = self.env['event.event'].create(event_vals)
        calendar_vals = {
            'partner': self.partner.id,
            'year': int(date_begin[0:4]),
            'dates': days}
        calendar = self.env['res.partner.calendar'].create(calendar_vals)
        for track in self.event.track_ids:
            for day in calendar.dates:
                if day.date == track.session_date:
                    track.presences[0].partner_calendar_day = day.id

    def test_hr_contract_finalized_event(self):
        expired_stage = self.env.ref('hr_contract_stages.stage_contract3')
        with self.assertRaises(exceptions.Warning):
            self.contract.contract_stage_id = expired_stage
        self.contract.date_end = (
            fields.Date.from_string(self.event.track_ids[0].session_date) +
            relativedelta(days=-1))
        self.contract.contract_stage_id = expired_stage
        for track in self.event.track_ids:
            self.assertEqual(
                track.presences[0].state, 'canceled',
                'Bad presence state for employee contract cancelation')
