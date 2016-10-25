# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _


class WizEventSubstitution(models.TransientModel):
    _name = 'wiz.event.substitution'
    _description = 'Wizard for substitution employee absences'

    holiday = fields.Many2one(
        comodel_name='hr.holidays', string="Absence")
    lines = fields.One2many(
        comodel_name='wiz.event.substitution.line',
        inverse_name='wiz', string='Events for substitution')

    @api.multi
    def button_substitution_employee(self):
        registration_obj = self.env['event.registration']
        event_obj = self.env['event.event']
        self.ensure_one()
        for line in self.lines:
            vals = {'event_id': line.event.id,
                    'partner_id': line.employee.address_home_id.id,
                    'replaces_to': self.holiday.employee_id.address_home_id.id}
            event_date = event_obj._convert_date_to_local_format_with_hour(
                line.event.date_begin).date()
            holiday_date = event_obj._convert_date_to_local_format_with_hour(
                self.holiday.date_from).date()
            if holiday_date < event_date:
                vals['date_start'] = line.event.date_begin
            else:
                start_time = event_obj._convert_times_to_float(
                    line.event.date_begin)
                vals['date_start'] = event_obj._put_utc_format_date(
                    holiday_date, start_time)
            event_date = event_obj._convert_date_to_local_format_with_hour(
                line.event.date_end).date()
            holiday_date = event_obj._convert_date_to_local_format_with_hour(
                self.holiday.date_to).date()
            if holiday_date > event_date:
                vals['date_end'] = line.event.date_end
            else:
                start_time = event_obj._convert_times_to_float(
                    line.event.date_end)
                vals['date_end'] = event_obj._put_utc_format_date(
                    holiday_date, start_time)
            registration = registration_obj.create(vals)
            if len(registration.contracts_permitted) == 1:
                registration.contract = registration.contracts_permitted[0].id
            m = ("<p> " + str(fields.Datetime.now()) + ': ' +
                 _('The employee: %s, replaces the employee: %s, from date %s,'
                   ' to date %s') %
                 (line.employee.address_home_id.name,
                  self.holiday.employee_id.address_home_id.name,
                  str(event_obj._convert_date_to_local_format_with_hour(
                      self.holiday.date_from).date()),
                  str(event_obj._convert_date_to_local_format_with_hour(
                      self.holiday.date_to).date())) + "<br>")
            m += "<br> <br>"
            vals = {'type': 'comment',
                    'model': 'event.event',
                    'record_name': line.event.name,
                    'res_id': line.event.id,
                    'body': m}
            self.env['mail.message'].create(vals)
        self.holiday.signal_workflow('validate')
        self.holiday._update_presences_validate_holiday()
        self.holiday._update_partner_calendar_day(
            self.holiday, absence_type=self.holiday.holiday_status_id.id)


class WizEventSubstitutionLine(models.TransientModel):
    _name = 'wiz.event.substitution.line'
    _description = 'Wizard Events for substitution'

    wiz = fields.Many2one(
        comodel_name='wiz.event.substitution', string='Wizard')
    event = fields.Many2one(comodel_name='event.event', string='Event')
    employee = fields.Many2one(comodel_name='hr.employee', string='Employee')
