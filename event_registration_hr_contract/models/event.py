# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from openerp.addons.event_track_assistant._common import\
    _convert_to_local_date, _convert_to_utc_date, _convert_time_to_float

datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.depends('date_begin')
    def _compute_date_begin_without_hour(self):
        tz = self.env.user.tz
        for event in self.filtered('date_begin'):
            event.date_begin_without_hour =\
                _convert_to_local_date(event.date_begin, tz=tz)

    @api.depends('date_end')
    def _compute_date_end_without_hour(self):
        tz = self.env.user.tz
        for event in self.filtered('date_end'):
            event.date_end_without_hour =\
                _convert_to_local_date(event.date_end, tz=tz)

    date_begin_without_hour = fields.Date(
        string='Date begin without hour', store=True,
        compute='_compute_date_begin_without_hour')
    date_end_without_hour = fields.Date(
        string='Date end without hour', store=True,
        compute='_compute_date_end_without_hour')


class EventRegistration(models.Model):
    _inherit = 'event.registration'

#    @api.depends('date_start', 'date_end', 'partner_id')
    def _compute_contracts_permitted(self):
        for registration in self:
            registration.contracts_permitted = [(6, 0, [])]
            if (registration.date_start and registration.date_end and
                    registration.partner_id):
                permitted_contracts = self._search_permitted_contracts(
                    registration)
                registration.contracts_permitted = [(6, 0,
                                                     permitted_contracts.ids)]

    contract = fields.Many2one('hr.contract', string='Employee contract')
    contract_stage = fields.Many2one(
        comodel_name='hr.contract.stage', string='Contract stage',
        related='contract.contract_stage_id', store=True)
    employee = fields.Many2one(
        'hr.employee', related='partner_id.employee_id',
        string='Employee', store=True)
    contracts_permitted = fields.Many2many(
        'hr.contract', string='Contracts permitted',
        compute='_compute_contracts_permitted')

    @api.onchange('partner_id')
    def _onchange_partner(self):
        result = super(EventRegistration, self)._onchange_partner()
        self.contract = False
        if self.partner_id:
            self._find_contracts_for_employee()
        return result

    @api.multi
    @api.onchange('date_start')
    def _onchange_date_start(self):
        self.ensure_one()
        res = super(EventRegistration, self)._onchange_date_start()
        if res:
            return res
        self._find_contracts_for_employee()
        return res

    @api.multi
    @api.onchange('date_end')
    def _onchange_date_end(self):
        self.ensure_one()
        res = super(EventRegistration, self)._onchange_date_end()
        if res:
            return res
        self._find_contracts_for_employee()
        return res

    @api.multi
    @api.onchange('contract')
    def _onchange_contract(self):
        self.ensure_one()
        tz = self.env.user.tz
        if self.contract:
            if not self.date_start:
                self.date_start = self.event_id.date_begin
            if not self.date_end:
                self.date_end = self.event_id.date_end
            from_date = date2str(_convert_to_local_date(
                self.date_start, tz=tz).date())
            if self.contract.date_start and\
                    self.contract.date_start > from_date:
                start_time = _convert_time_to_float(self.date_start, tz=tz)
                self.date_start = _convert_to_utc_date(
                    self.contract.date_start, start_time, tz=tz)
            to_date = date2str(_convert_to_local_date(
                self.date_end, tz=tz).date())
            if self.contract.date_end and self.contract.date_end < to_date:
                end_time = _convert_time_to_float(self.date_end, tz=tz)
                self.date_end = _convert_to_utc_date(
                    self.contract.date_end, end_time, tz=tz)

    def _find_contracts_for_employee(self):
        tz = self.env.user.tz
        permitted_contracts = self._search_permitted_contracts(self)
        self.contracts_permitted = [(6, 0, permitted_contracts.ids)]
        if len(permitted_contracts) == 1:
            self.contract = permitted_contracts[0].id
            from_date = date2str(_convert_to_local_date(
                self.date_start, tz=tz).date())
            if self.contract.date_start > from_date:
                start_time = _convert_time_to_float(self.date_start, tz=tz)
                self.date_start = _convert_to_utc_date(
                    self.contract.date_start, start_time, tz=tz)
            to_date = date2str(_convert_to_local_date(
                self.date_end, tz=tz).date())
            if self.contract.date_end and self.contract.date_end < to_date:
                end_time = _convert_time_to_float(self.date_end, tz=tz)
                self.date_end = _convert_to_utc_date(
                    self.contract.date_end, end_time, tz=tz)

    def _search_permitted_contracts(self, registration):
        contract_obj = self.env['hr.contract']
        permitted_contracts = self.env['hr.contract']
        tz = self.env.user.tz
        if not registration.date_start:
            registration.date_start = registration.event_id.date_begin
        if not registration.date_end:
            registration.date_end = registration.event_id.date_end
        date_start = date2str(_convert_to_local_date(
            registration.date_start, tz=tz).date())
        date_end = date2str(_convert_to_local_date(
            registration.date_end, tz=tz).date())
        cond = contract_obj._search_contracts_without_date_end(
            registration.partner_id, date_end)
        contracts = contract_obj.search(cond)
        for contract in contracts:
            if contract not in permitted_contracts:
                permitted_contracts += contract
        cond = contract_obj._search_contracts_with_date_end(
            registration.partner_id, date_start, date_end)
        contracts = contract_obj.search(cond)
        for contract in contracts:
            if contract not in permitted_contracts:
                permitted_contracts += contract
        return permitted_contracts

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        wiz_vals.update({'contract': self.contract.id})
        return wiz_vals

    @api.multi
    def button_registration_open(self):
        self.ensure_one()
        if self.employee and not self.contract:
            raise exceptions.Warning(
                _("You must enter the employee's contract"))
        return super(EventRegistration, self).button_registration_open()


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    contract = fields.Many2one('hr.contract', string='Employee contract')

    def _update_employee_calendar_days(
            self, contract=False, cancel_presence=False):
        tz = self.env.user.tz
        holidays_obj = self.env['hr.holidays']
        day = self.partner_calendar_day
        if not day:
            raise exceptions.Warning(
                _('Calendar not found for employee %s')
                % self.partner.name)
        if contract:
            day.contract = contract.id
        if self.absence_type:
            day.write({'festive': True,
                       'absence_type': self.absence_type.id})
        if cancel_presence:
            day.write({'festive': False,
                       'absence_type': False})
            if day.absence_type_from_employee_contract:
                absence_type = day.absence_type_from_employee_contract
                day.write({'festive': True,
                           'absence_type': absence_type.id})
        presence_date = datetime2str(_convert_to_utc_date(
            self.session_date_without_hour, time=0.0, tz=tz))
        cond = [('employee_id', '=', self.partner.id),
                ('date_from', '>=', presence_date),
                ('date_to', '<=', presence_date),
                ('type', '=', 'remove'),
                ('state', '=', 'validate')]
        holiday = holidays_obj.search(cond, limit=1)
        if holiday:
            day.write({'absence': True,
                       'absence_type': holiday.holiday_status_id.id})
