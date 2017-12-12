# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import threading
import openerp
from openerp import models, fields, api, exceptions, _
from openerp.addons.event_track_assistant._common import\
    _convert_to_local_date, _convert_to_utc_date, _convert_time_to_float
date2str = fields.Date.to_string


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
        tz = self.env.user.tz
        self._validate_employee_calendar(
            _convert_to_local_date(self.holiday.date_from, tz=tz).year,
            _convert_to_local_date(self.holiday.date_to, tz=tz).year,
            self.holiday.employee_id.address_home_id)
        for line in self.lines:
            vals = self._validate_employee_contract_and_registration(line)
            self._validate_employee_calendar(
                vals.get('date_start').year, vals.get('date_end').year,
                line.employee.address_home_id)
        threaded_calculation = threading.Thread(
            target=self.button_substitution_employee_from_thread)
        threaded_calculation.start()

    def _validate_employee_contract_and_registration(self, line):
        tz = self.env.user.tz
        contract_obj = self.env['hr.contract']
        vals = self._prepare_dates_for_registration(line)
        date_from = _convert_to_local_date(
            vals.get('date_start'), tz=tz).date()
        date_to = _convert_to_local_date(
            vals.get('date_end'), tz=tz).date()
        cond = contract_obj._search_contracts_without_date_end(
            line.employee.address_home_id, date_from)
        permitted_contracts = contract_obj.search(cond)
        cond = contract_obj._search_contracts_with_date_end(
            line.employee.address_home_id, date_to, date_from)
        permitted_contracts += contract_obj.search(cond)
        if not permitted_contracts:
            raise exceptions.Warning(
                _("Employee %s without contract for event %s") %
                (line.employee.name, line.event.name))
        registrations = line.event.registration_ids.filtered(
            lambda x: x.partner_id and x.date_start and
            x.date_end and x.state in ('done', 'open') and
            x.partner_id.id == line.employee.address_home_id.id and
            ((str(vals.get('date_end')) >= x.date_start and
              str(vals.get('date_end')) <= x.date_end) or
             (str(vals.get('date_start')) <= x.date_end and
              str(vals.get('date_start')) >= x.date_start)))
        if registrations:
            raise exceptions.Warning(
                _('You can not confirm this registration, because their '
                  'dates overlap with another record of the same employee,'
                  ' in event: %s') % (line.event.name))
        return vals

    def _validate_employee_calendar(self, from_year, to_year, partner):
        partner_calendar_obj = self.env['res.partner.calendar']
        for year in range(from_year, to_year+1):
            cond = [('partner', '=', partner.id),
                    ('year', '=', year)]
            if not partner_calendar_obj.search(cond):
                raise exceptions.Warning(
                    _('Employee %s without calendar') % (partner.name))

    def button_substitution_employee_from_thread(self):
        with openerp.api.Environment.manage():
            with openerp.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(
                    new_cr, self.env.uid, self.env.context)
                self.with_env(new_env).substitution_employee_from_thread()
                new_env.cr.commit()

    def substitution_employee_from_thread(self):
        registration_obj = self.env['event.registration']
        presence_obj = self.env['event.track.presence']
        registrations = self.env['event.registration']
        wiz_obj = self.env['wiz.event.registration.confirm']
        wiz = wiz_obj.create({'name': 'Confirm registration'})
        tz = self.env.user.tz
        self.ensure_one()
        for line in self.lines:
            vals_reg = self._prepare_dates_for_registration(line)
            registration = registration_obj.create(vals_reg)
            if line.confirm_registration:
                registrations += registration
            if len(registration.contracts_permitted) == 1:
                registration.contract = registration.contracts_permitted[0].id
            m = ("<p> " + fields.Date.context_today(self) + ': ' +
                 _('The employee: %s, replaces the employee: %s, from date %s,'
                   ' to date %s') %
                 (line.employee.address_home_id.name,
                  self.holiday.employee_id.address_home_id.name,
                  date2str(_convert_to_local_date(
                      self.holiday.date_from, tz=tz)),
                  date2str(_convert_to_local_date(
                      self.holiday.date_to, tz=tz))) + "<br>")
            m += "<br> <br>"
            vals = {'type': 'comment',
                    'model': 'event.event',
                    'record_name': line.event.name,
                    'res_id': line.event.id,
                    'body': m}
            self.env['mail.message'].create(vals)
            cond = [('event', '=', vals_reg.get('event_id')),
                    ('partner', '=',
                     self.holiday.employee_id.address_home_id.id),
                    ('session_date_without_hour', '>=',
                     vals_reg.get('date_start').date()),
                    ('session_date_without_hour', '<=',
                     vals_reg.get('date_end').date())]
            presences = presence_obj.search(cond)
            presences.write({'state': 'canceled'})
        self.holiday.signal_workflow('validate')
        self.holiday._update_presences_validate_holiday()
        self.holiday._update_partner_calendar_day(
            self.holiday, absence_type=self.holiday.holiday_status_id.id)
        wiz.with_context(
            {'active_ids':
             registrations.ids}).action_confirm_registrations()

    def _prepare_dates_for_registration(self, line):
        tz = self.env.user.tz
        vals = {'event_id': line.event.id,
                'partner_id': line.employee.address_home_id.id,
                'replaces_to': self.holiday.employee_id.address_home_id.id}
        start_time = _convert_time_to_float(line.event.date_begin, tz=tz)
        vals['date_start'] = max(
            _convert_to_utc_date(
                _convert_to_local_date(line.event.date_begin, tz=tz).date(),
                start_time, tz=tz),
            _convert_to_utc_date(
                _convert_to_local_date(self.holiday.date_from, tz=tz).date(),
                start_time, tz=tz))
        end_time = _convert_time_to_float(line.event.date_end, tz=tz)
        vals['date_end'] = min(
            _convert_to_utc_date(
                _convert_to_local_date(line.event.date_end, tz=tz).date(),
                end_time, tz=tz),
            _convert_to_utc_date(
                _convert_to_local_date(self.holiday.date_to, tz=tz).date(),
                end_time, tz=tz))
        return vals


class WizEventSubstitutionLine(models.TransientModel):
    _name = 'wiz.event.substitution.line'
    _description = 'Wizard Events for substitution'

    wiz = fields.Many2one(
        comodel_name='wiz.event.substitution', string='Wizard')
    confirm_registration = fields.Boolean(
        string='Confirm substitute registration', default=True)
    event = fields.Many2one(comodel_name='event.event', string='Event')
    employee = fields.Many2one(comodel_name='hr.employee', string='Employee')
