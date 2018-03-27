# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta


class TestHrTimesheetSheetEventHours(common.TransactionCase):

    def setUp(self):
        super(TestHrTimesheetSheetEventHours, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Partner for test crm claim event presence',
            'is_company': True})
        self.employee = self.browse_ref('hr.employee_al')
        self.user = self.env['res.users'].create(
            {'name': 'aaaaa',
             'login': 'aaaaa@aaaa.com'})
        self.employee.write({'address_home_id': self.partner.id,
                             'user_id': self.user.id})
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
            date_begin = fields.Date.to_string(fields.Date.from_string(
                date_begin) + relativedelta(days=1))
            date_begin = '{} 10:00:00'.format(date_begin)
            contador += 1
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=4))
        date_end = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=10))
        event_vals = {'name': 'Test crm claim event presence',
                      'date_begin': date_begin,
                      'date_end': date_end,
                      'track_ids': tracks}
        self.event = self.env['event.event'].create(event_vals)

    def test_hrTimesheet_sheet_event_hours(self):
        date_begin = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=4))
        date_end = fields.Date.to_string(fields.Date.from_string(
            fields.Date.today()) + relativedelta(days=10))
        sheet_vals = {
            'employee_id': self.employee.id,
            'date_from': date_begin[0:10],
            'date_to': date_end[0:10]}
        sheet = self.env['hr_timesheet_sheet.sheet'].create(sheet_vals)
        self.assertEqual(
            sheet.month_hours, 10.0, 'Bad working hours')
