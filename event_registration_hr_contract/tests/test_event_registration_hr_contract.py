# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields


class TestEventRegistrationHrContract(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationHrContract, self).setUp()
        self.calendar_model = self.env['res.partner.calendar']
        self.contract_model = self.env['hr.contract']
        self.holiday_model = self.env['calendar.holiday']
        self.account_model = self.env['account.analytic.account']
        self.project_model = self.env['project.project']
        self.sale_model = self.env['sale.order']
        self.event_model = self.env['event.event']
        self.wiz_model = self.env['wiz.calculate.workable.festive']
        self.registration_model = self.env['event.registration']
        self.calc_calendar_model = self.env['wiz.calculate.employee.calendar']
        self.employee = self.env.ref('hr.employee')
        self.hr_holidays_model = self.env['hr.holidays']
        self.employee.address_home_id = self.ref('base.public_partner')
        calendar_line_vals = {
            'date': '2020-03-17',
            'absence_type': self.ref('hr_holidays.holiday_status_comp')}
        calendar_vals = {'name': 'Holidays calendar',
                         'lines': [(0, 0, calendar_line_vals)]}
        self.calendar_holiday = self.holiday_model.create(calendar_vals)
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2020-03-01',
                        'date': '2020-03-31',
                        'festive_calendars':
                        [(6, 0, [self.calendar_holiday.id])]}
        self.account = self.account_model.create(account_vals)
        project_vals = {'name': 'project 1',
                        'analytic_account_id': self.account.id}
        self.project = self.project_model.create(project_vals)
        service_product = self.env.ref('product.product_product_consultant')
        service_product.write({'performance': 5.0,
                               'recurring_service': True})
        service_product.performance = 5.0
        service_product.route_ids = [
            (6, 0,
             [self.ref('procurement_service_project.route_serv_project')])]
        sale_vals = {
            'name': 'sale order 1300',
            'partner_id': self.ref('base.res_partner_1'),
            'partner_shipping_id': self.ref('base.res_partner_1'),
            'partner_invoice_id': self.ref('base.res_partner_1'),
            'pricelist_id': self.env.ref('product.list0').id,
            'project_id': self.account.id,
            'project_by_task': 'no'}
        sale_line_vals = {
            'product_id': service_product.id,
            'start_date': '2016-03-01',
            'start_hour': 5.0,
            'end_hour': 10.0,
            'end_date': '2016-03-31',
            'name': service_product.name,
            'product_uom_qty': 7,
            'product_uos_qty': 7,
            'product_uom': service_product.uom_id.id,
            'price_unit': service_product.list_price,
            'performance': 5.0,
            'march': True,
            'week4': True,
            'tuesday': True}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)
        contract_vals = {'name': 'Contract 1',
                         'employee_id': self.employee.id,
                         'partner': self.ref('base.public_partner'),
                         'type_id':
                         self.ref('hr_contract.hr_contract_type_emp'),
                         'wage': 500,
                         'date_start': '2020-02-01',
                         'working_hours':
                         self.ref('resource.timesheet_group1')}
        self.contract = self.contract_model.create(contract_vals)
        wiz_vals = {'year': 2020}
        wiz = self.wiz_model.create(wiz_vals)
        wiz.with_context(
            {'active_id':
             self.contract.id}).button_calculate_workables_and_festives()

    def test_event_registration_hr_contract(self):
        holiday_vals = {
            'name': 'Administrator',
            'holiday_type': 'employee',
            'holiday_status_id': self.ref('hr_holidays.holiday_status_sl'),
            'employee_id': self.employee.id,
            'date_from': '2020-03-15 05:00:00',
            'date_to': '2020-03-20 10:00:00',
            'type': 'remove'}
        self.holidays = self.hr_holidays_model.create(holiday_vals)
        self.holidays.signal_workflow('confirm')
        wiz_vals = {'validate_ausence': True,
                    'ausence': self.holidays.id}
        calculate_calendar = self.calc_calendar_model.create(wiz_vals)
        calculate_calendar.button_calculate_employee_calendar()
        self.holidays.signal_workflow('validate')
        self.holidays.signal_workflow('refuse')

    def test_wiz_event_registration_contract_confirm(self):
        cond = [('event_id', '!=', False),
                ('state', '=', 'draft')]
        registration = self.registration_model.search(cond, limit=1)
        registration.write({'date_start': registration.event_id.date_begin,
                            'date_end': registration.event_id.date_end})
        registration.date_start = registration.event_id.date_begin
        registration.date_end = registration.event_id.date_end
        reg_confirm_model = self.env['wiz.event.registration.confirm']
        wiz = reg_confirm_model.create({'name': 'test from assistant'})
        res = wiz._prepare_data_confirm_assistant(registration)
        self.assertIn(
            'contract', res, 'No contract in partner registration')
        registration.employee = self.employee.id
        date_begin = fields.Datetime.to_string(
            fields.Datetime.from_string(registration.date_start).date())
        track = {'name': date_begin,
                 'date': date_begin,
                 'event_id': registration.event_id.id,
                 'duration': 2,
                 'presences': [(0, 0, {'partner': registration.partner_id.id,
                                       'name': registration.partner_id.name,
                                       'session_duration': 2,
                                       'session_date': date_begin,
                                       'contract': self.contract.id,
                                       'employee': self.employee.id,
                                       'employee_id': self.employee.id})]}
        track = self.env['event.track'].create(track)
        date_begin = fields.Datetime.from_string(registration.date_start)
        calendar_vals = {'partner': registration.partner_id.id,
                         'year': date_begin.year}
        calendar_line_vals = {
            'partner': registration.partner_id.id,
            'date': registration.event_id.track_ids[0].date,
            'contract': self.contract.id,
            'festive': False}
        calendar_vals['dates'] = [(0, 0, calendar_line_vals)]
        calendar = self.calendar_model.create(calendar_vals)
        presence = registration.event_id.track_ids[0].presences[0]
        presence.partner_calendar_day = calendar.dates[0].id
        registration._cancel_presences(
            fields.Datetime.to_string(
                fields.Datetime.from_string(registration.date_start).date()),
            fields.Datetime.to_string(
                fields.Datetime.from_string(registration.date_end).date()),
            'notes')
        self.assertEquals(
            track.presences[0].state, 'canceled', 'BAD state for presence')
