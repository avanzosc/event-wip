# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import exceptions, fields


class TestCalendarHoliday(common.TransactionCase):

    def setUp(self):
        super(TestCalendarHoliday, self).setUp()
        self.holiday_model = self.env['calendar.holiday']
        self.registration_model = self.env['event.registration']
        self.contract_model = self.env['hr.contract']
        self.calendar_model = self.env['res.partner.calendar']
        self.wiz_model = self.env['wiz.calculate.workable.festive']
        self.holidays_model = self.env['hr.holidays']
        self.substitution_model = self.env['wiz.event.substitution']
        self.today = fields.Date.from_string(fields.Date.today())
        calendar_line_vals = {
            'date': '2016-01-06',
            'absence_type': self.ref('hr_holidays.holiday_status_comp')}
        calendar_vals = {'name': 'Holidays calendar',
                         'lines': [(0, 0, calendar_line_vals)]}
        self.calendar_holiday = self.holiday_model.create(calendar_vals)
        contract_vals = {'name': 'Contract 1',
                         'employee_id': self.ref('hr.employee'),
                         'partner': self.ref('base.public_partner'),
                         'type_id':
                         self.ref('hr_contract.hr_contract_type_emp'),
                         'wage': 500,
                         'date_start': '2016-01-02',
                         'holiday_calendars':
                         [(6, 0, [self.calendar_holiday.id])]}
        self.contract = self.contract_model.create(contract_vals)
        self.env.ref('hr.employee').address_home_id = (
            self.ref('base.public_partner'))
        self.env.ref('base.public_partner').employee_id = (
            self.ref('hr.employee'))

    def test_calendar_holiday(self):
        self.calendar_holiday.lines[0].write({'date': '2016-01-06'})
        wiz = self.wiz_model.with_context(
            {'active_id': self.contract.id}).create({'year': self.today.year})
        vals = ['year']
        wiz.with_context(
            {'active_id': self.contract.id}).default_get(vals)
        wiz.with_context(
            {'active_id':
             self.contract.id}).button_calculate_workables_and_festives()
        cond = [('partner', '=', self.ref('base.public_partner')),
                ('year', '=', self.today.year)]
        calendar = self.calendar_model.search(cond)
        self.assertNotEqual(
            len(calendar), 0, 'Calendar not generated for partner')
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
        })
        self.user = self.env['res.users'].create({
            'partner_id': self.partner.id,
            'login': 'user',
            'password': 'pass',
        })
        employee_vals = {
            'name': 'Test Employee',
            'user_id': self.user.id,
            'address_home_id': self.partner.id
        }
        employee_vals.update(
            self.env['hr.employee'].onchange_user(
                user_id=employee_vals['user_id'])['value'])
        self.employee = self.env['hr.employee'].create(employee_vals)
        self.partner.employee_id = self.employee.id
        contract_vals = {'name': 'Contract 2',
                         'employee_id': self.employee.id,
                         'partner': self.partner.id,
                         'type_id':
                         self.ref('hr_contract.hr_contract_type_emp'),
                         'wage': 500,
                         'date_start': '2016-01-02',
                         'holiday_calendars':
                         [(6, 0, [self.calendar_holiday.id])]}
        self.contract2 = self.contract_model.create(contract_vals)
        wiz = self.wiz_model.with_context(
            {'active_id': self.contract2.id}).create({'year': self.today.year})
        vals = ['year']
        wiz.with_context(
            {'active_id': self.contract2.id}).default_get(vals)
        wiz.with_context(
            {'active_id':
             self.contract2.id}).button_calculate_workables_and_festives()
        event = self.env.ref('event.event_0')
        reg_vals = {
            'partner_id': self.ref('base.public_partner'),
            'name': 'aaaaaaa',
            'date_start': event.date_begin,
            'date_end': event.date_end,
            'contract': self.contract.id,
            'employee': self.ref('hr.employee')}
        event.registration_ids = [(0, 0, reg_vals)]
        event.track_ids[0].write({'date': event.date_begin})
        event.track_ids[0].presences = [
            (0, 0, {'name': 'a', 'partner': self.ref('base.public_partner')})]
        employee3 = self.browse_ref('hr.employee')
        employee3.address_home_id.email = 'employee3@odoo.com'
        self.employee.address_home_id.email = 'employee@odoo.com'
        hr_holidays_vals = {'name': 'Employee holidays',
                            'holiday_type': 'employee',
                            'holiday_status_id':
                            self.ref('hr_holidays.holiday_status_comp'),
                            'employee_id': employee3.id,
                            'date_from': '2016-01-01 00:00:00',
                            'date_to': '2025-01-01 00:00:00',
                            'number_of_days_temp': 1}
        hr_holidays = self.holidays_model.create(hr_holidays_vals)
        wiz_vals = {
            'holiday': hr_holidays.id,
            'lines': [(0, 0, {'confirm_registration': True,
                              'event': event.id,
                              'employee': self.employee.id})]}
        wiz = self.substitution_model.create(wiz_vals)
        wiz._validate_employee_contract_and_registration(wiz.lines[0])
        wiz._validate_employee_calendar(
            self.today.year, self.today.year, self.partner)
        wiz.substitution_employee_from_thread()
        with self.assertRaises(exceptions.MissingError):
            wiz.button_substitution_employee_from_thread()
        cond = [('partner', '=', hr_holidays.employee_id.address_home_id.id),
                ('year', '=', self.today.year)]
        calendar = self.calendar_model.search(cond)
        calendar.unlink()
        with self.assertRaises(exceptions.Warning):
            wiz.button_substitution_employee()
        with self.assertRaises(exceptions.Warning):
            wiz._validate_employee_contract_and_registration(wiz.lines[0])
        self.contract2.unlink()
        with self.assertRaises(exceptions.Warning):
            wiz._validate_employee_contract_and_registration(wiz.lines[0])

    def test_wiz_event_registration_confirm(self):
        cond = [('event_id', '!=', False),
                ('state', '=', 'draft')]
        registration = self.registration_model.search(cond, limit=1)
        registration.write({'date_start': registration.event_id.date_begin,
                            'date_end': registration.event_id.date_end,
                            'replaces_to': registration.partner_id.id})
        registration.date_start = registration.event_id.date_begin
        registration.date_end = registration.event_id.date_end
        track_vals = {'name': registration.name,
                      'event_id': registration.event_id.id,
                      'date': registration.date_start,
                      'duration': 1}
        track = self.env['event.track'].create(track_vals)
        reg_confirm_model = self.env['wiz.event.registration.confirm']
        wiz = reg_confirm_model.create({'name': 'test from assistant'})
        res = wiz._prepare_data_confirm_assistant(registration)
        self.assertEqual(
            res.get('replaces_to'), registration.partner_id.id,
            'Bad replaces_to in registration')
        wiz.with_context(
            active_ids=registration.ids).action_confirm_registrations()
        self.assertEqual(
            track.presences[0].replaces_to.id, registration.partner_id.id,
            'Bad replaces_to in presences')
