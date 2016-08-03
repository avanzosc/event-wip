# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class WizCalculateEmployeeCalendar(models.TransientModel):
    _name = 'wiz.calculate.employee.calendar'
    _description = 'Wizard for calculate employee calendar'

    validate_ausence = fields.Boolean(string='Validate ausence')
    ausence = fields.Many2one(
        comodel_name='hr.holidays', string='Absence')

    @api.multi
    def button_calculate_employee_calendar(self):
        self.ensure_one()
        partner_calendar_obj = self.env['res.partner.calendar']
        event_obj = self.env['event.event']
        from_year = int(event_obj._convert_date_to_local_format_with_hour(
            self.ausence.date_from).strftime('%Y'))
        to_year = int(event_obj._convert_date_to_local_format_with_hour(
            self.ausence.date_to).strftime('%Y'))
        while from_year <= to_year:
            partner = self.ausence.employee_id.address_home_id
            cond = [('partner', '=', partner.id),
                    ('year', '=', from_year)]
            calendar = partner_calendar_obj.search(cond)
            if not calendar:
                self._generate_calendar(partner, from_year)
            from_year += 1
        if self.validate_ausence:
            self.ausence.signal_workflow('validate')
            self.ausence._update_presences_validate_holiday()
            self.ausence._update_partner_calendar_day(
                self.ausence, absence_type=self.ausence.holiday_status_id.id)
        else:
            self.ausence._update_presences_refuse_holiday()
            self.ausence._update_partner_calendar_day(self.ausence)
            self.ausence.signal_workflow('refuse')

    def _generate_calendar(self, partner, year):
        contract_obj = self.env['hr.contract']
        event_obj = self.env['event.event']
        partner._generate_calendar(year)
        date_start = event_obj._convert_date_to_local_format_with_hour(
            self.ausence.date_from).date().strftime('%Y-%m-%d')
        cond = [('employee_id', '=', self.ausence.employee_id.id), '|',
                ('date_end', '=', False),
                ('date_end', '>', date_start)]
        contracts = contract_obj.search(cond)
        contracts = contract_obj.search(cond)
        for contract in contracts:
            if (contract.working_hours and
                    contract.working_hours.attendance_ids):
                contract.partner._put_estimated_hours_in_calendar(year,
                                                                  contract)
            for calendar in contract.holiday_calendars:
                partner._generate_festives_in_calendar(year, calendar)
