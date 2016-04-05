# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.depends('date_begin')
    def _calculate_date_begin_without_hour(self):
        for event in self:
            event.date_begin_without_hour = False
            if event.date_begin:
                new_date = event._convert_date_to_local_format_with_hour(
                    event.date_begin).strftime('%Y-%m-%d')
                event.date_begin_without_hour = new_date

    @api.depends('date_end')
    def _calculate_date_end_without_hour(self):
        event_obj = self.env['event.event']
        for event in self:
            event.date_end_without_hour = False
            if event.date_end:
                new_date = event_obj._convert_date_to_local_format_with_hour(
                    event.date_end).strftime('%Y-%m-%d')
                event.date_end_without_hour = new_date

    date_begin_without_hour = fields.Date(
        'Date begin without hour', store=True,
        compute='_calculate_date_begin_without_hour')
    date_end_without_hour = fields.Date(
        'Date end without hour', store=True,
        compute='_calculate_date_end_without_hour')


class EventRegistration(models.Model):
    _inherit = 'event.registration'

#    @api.depends('date_start', 'date_end', 'partner_id')
    def _calculate_contracts_permited(self):
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
        'hr.employee', related='partner_id.employee',
        string='Employee', store=True)
    contracts_permitted = fields.Many2many(
        'hr.contract', string='Contracts permitted',
        compute='_calculate_contracts_permited')

    @api.onchange('partner_id')
    def _onchange_partner(self):
        super(EventRegistration, self)._onchange_partner()
        self.contract = False
        if self.partner_id:
            self._find_contracts_for_employee()

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
        event_obj = self.env['event.event']
        if self.contract:
            if not self.date_start:
                self.date_start = self.event_id.date_begin
            if not self.date_end:
                self.date_end = self.event_id.date_end
            from_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_start).date().strftime('%Y-%m-%d')
            if self.contract.date_start > from_date:
                start_time = event_obj._convert_times_to_float(self.date_start)
                self.date_start = event_obj._put_utc_format_date(
                    self.contract.date_start, start_time)
            to_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_end).date().strftime('%Y-%m-%d')
            if self.contract.date_end and self.contract.date_end < to_date:
                end_time = event_obj._convert_times_to_float(self.date_end)
                self.date_end = event_obj._put_utc_format_date(
                    self.contract.date_end, end_time)

    def _find_contracts_for_employee(self):
        event_obj = self.env['event.event']
        permitted_contracts = self._search_permitted_contracts(self)
        self.contracts_permitted = [(6, 0, permitted_contracts.ids)]
        if len(permitted_contracts) == 1:
            self.contract = permitted_contracts[0].id
            from_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_start).date().strftime('%Y-%m-%d')
            if self.contract.date_start > from_date:
                start_time = event_obj._convert_times_to_float(self.date_start)
                self.date_start = event_obj._put_utc_format_date(
                    self.contract.date_start, start_time)
            to_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_end).date().strftime('%Y-%m-%d')
            if self.contract.date_end and self.contract.date_end < to_date:
                end_time = event_obj._convert_times_to_float(self.date_end)
                self.date_end = event_obj._put_utc_format_date(
                    self.contract.date_end, end_time)

    def _search_permitted_contracts(self, registration):
        contract_obj = self.env['hr.contract']
        permitted_contracts = self.env['hr.contract']
        event_obj = self.env['event.event']
        if not registration.date_start:
            registration.date_start = registration.event_id.date_begin
        if not registration.date_end:
            registration.date_end = registration.event_id.date_end
        date_start = event_obj._convert_date_to_local_format_with_hour(
            registration.date_start).date().strftime('%Y-%m-%d')
        date_end = event_obj._convert_date_to_local_format_with_hour(
            registration.date_end).date().strftime('%Y-%m-%d')
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

    @api.multi
    def registration_open(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.append.assistant']
        if self.employee and not self.contract:
            raise exceptions.Warning(
                _("You must enter the employee's contract"))
        result = super(EventRegistration, self).registration_open()
        wiz = wiz_obj.browse(result['res_id'])
        if self.contract:
            wiz.write({'contract': self.contract.id})
        return result


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    contract = fields.Many2one('hr.contract', string='Employee contract')

    def _update_employee_calendar_days(self, contract=False,
                                       cancel_presence=False):
        holidays_obj = self.env['hr.holidays']
        event_obj = self.env['event.event']
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
        presence_date = event_obj._put_utc_format_date(
            self.session_date_without_hour, 0.0).strftime(
            '%Y-%m-%d %H:%M:%S')
        cond = [('employee_id', '=', self.partner.id),
                ('date_from', '>=', presence_date),
                ('date_to', '<=', presence_date),
                ('type', '=', 'remove'),
                ('state', '=', 'validate')]
        holiday = holidays_obj.search(cond, limit=1)
        if holiday:
            day.write({'absence': True,
                       'absence_type': holiday.holiday_status_id.id})
