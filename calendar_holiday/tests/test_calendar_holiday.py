# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields


class TestCalendarHoliday(common.TransactionCase):

    def setUp(self):
        super(TestCalendarHoliday, self).setUp()
        self.holiday_model = self.env['calendar.holiday']
        self.contract_model = self.env['hr.contract']
        self.calendar_model = self.env['res.partner.calendar']
        self.wiz_model = self.env['wiz.calculate.workable.festive']
        self.holidays_model = self.env['hr.holidays']
        self.today = fields.Date.from_string(fields.Date.today())
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.user = self.env['res.users'].create({
            'partner_id': self.partner.id,
            'login': 'user',
            'password': 'pass',
        })
        employee_model = self.env['hr.employee']
        employee_vals = {
            'name': 'Test Employee',
            'user_id': self.user.id,
        }
        employee_vals.update(
            employee_model.onchange_user(
                user_id=employee_vals['user_id'])['value'])
        self.employee = employee_model.create(employee_vals)
        calendar_line_vals = {
            'date': self.today.replace(month=1, day=6),
            'absence_type': self.ref('hr_holidays.holiday_status_comp'),
        }
        calendar_vals = {
            'name': 'Holidays calendar',
            'lines': [(0, 0, calendar_line_vals)],
        }
        self.calendar_holiday = self.holiday_model.create(calendar_vals)
        contract_vals = {
            'name': 'Test Employee Contract',
            'date_start': self.today.replace(month=1, day=1),
            'date_end': self.today.replace(
                year=self.today.year+1, month=12, day=31),
            'employee_id': self.employee.id,
            'wage': 500,
            'working_hours': self.ref('resource.timesheet_group1'),
            'holiday_calendars': [(6, 0, [self.calendar_holiday.id])],
        }
        self.contract = self.contract_model.create(contract_vals)

    def test_calendar_holiday(self):
        cond = [('partner', '=', self.contract.partner.id),
                ('year', '=', self.today.year)]
        calendar = self.calendar_model.search(cond)
        self.assertEquals(len(calendar), 0)
        wiz = self.wiz_model.with_context(
            active_id=self.contract.id).create({})
        self.assertEquals(
            wiz.year, fields.Date.from_string(self.contract.date_start).year)
        wiz.button_calculate_workables_and_festives()
        calendar = self.calendar_model.search(cond)
        self.assertNotEquals(len(calendar), 0)
        wiz_vals = self.wiz_model.with_context(
            active_id=self.contract.id).default_get([])
        self.assertFalse(wiz_vals.get('year'))
        wiz2 = self.wiz_model.with_context(active_id=self.contract.id).create(
            {'year': fields.Date.from_string(self.contract.date_end).year})
        wiz2.button_calculate_workables_and_festives()
        date_to = str(fields.Datetime.from_string(
            fields.Datetime.now()).replace(month=1, day=7))
        date_from = str(fields.Datetime.from_string(
            fields.Datetime.now()).replace(month=1, day=1))
        vals = self.holidays_model.onchange_date_from(
            date_to, date_from, self.employee.id)
        days = int(vals['value'].get('number_of_days_temp'))
        self.assertEqual(days, 6, 'Absent days(1) badly calculated')
        vals = self.holidays_model.onchange_date_to(
            date_to, date_from, self.employee.id)
        days = int(vals['value'].get('number_of_days_temp'))
        self.assertEqual(days, 6, 'Absent days(2) badly calculated')
        vals = self.holidays_model.onchange_employee(
            self.employee.id, date_to, date_from)
        days = int(vals['value'].get('number_of_days_temp'))
        self.assertEqual(days, 6, 'Absent days(3) badly calculated')
