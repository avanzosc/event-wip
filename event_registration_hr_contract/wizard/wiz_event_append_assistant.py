# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    contract = fields.Many2one(
        comodel_name='hr.contract', string='Employee contract')
    employee = fields.Many2one(
        comodel_name='hr.employee', related='partner.employee_id',
        string='Employee')
    contracts_permitted = fields.Many2many(
        comodel_name='hr.contract', string='Contracts permitted')

    @api.multi
    @api.onchange('from_date', 'to_date', 'partner')
    def onchange_dates_and_partner(self):
        self.ensure_one()
        self.contract = False
        res = super(WizEventAppendAssistant, self).onchange_dates_and_partner()
        if not res:
            self._find_contracts_for_employee()
        return res

    @api.multi
    @api.onchange('contract')
    def _onchange_contract(self):
        self.ensure_one()
        if self.contract:
            self._put_init_dates_in_wizard()
            if self.contract.date_start > self.from_date:
                self.from_date = self.contract.date_start
            if (self.contract.date_end and
                    self.contract.date_end < self.to_date):
                self.to_date = self.contract.date_end

    def _find_contracts_for_employee(self):
        contract_obj = self.env['hr.contract']
        permitted_contracts = self.env['hr.contract']
        self._put_init_dates_in_wizard()
        cond = contract_obj._search_contracts_without_date_end(
            self.partner, self.to_date)
        contracts = contract_obj.search(cond)
        for contract in contracts:
            if contract not in permitted_contracts:
                permitted_contracts += contract
        cond = contract_obj._search_contracts_with_date_end(
            self.partner, self.from_date, self.to_date)
        contracts = contract_obj.search(cond)
        for contract in contracts:
            if contract not in permitted_contracts:
                permitted_contracts += contract
        self.contracts_permitted = [(6, 0, permitted_contracts.ids)]
        if len(permitted_contracts) == 1:
            self.contract = permitted_contracts[0].id
            if self.contract.date_start > self.from_date:
                self.from_date = self.contract.date_start
            if (self.contract.date_end and
                    self.contract.date_end < self.to_date):
                self.to_date = self.contract.date_end

    def _put_init_dates_in_wizard(self):
        if not self.from_date:
            self.from_date = self.min_from_date
        if not self.to_date:
            self.to_date = self.max_to_date

    def _prepare_registration_data(self, event):
        vals = super(WizEventAppendAssistant,
                     self)._prepare_registration_data(event)
        if self.contract:
            vals['contract'] = self.contract.id
        return vals

    def _create_presence_from_wizard(self, track, event):
        presence = super(WizEventAppendAssistant,
                         self)._create_presence_from_wizard(track, event)
        day = presence.partner_calendar_day
        if not day.absence_type_from_employee_contract:
            presence.absence_type = track.absence_type
        if self.contract:
            presence.contract = self.contract.id
        if self.employee:
            presence._update_employee_calendar_days(
                contract=self.contract, cancel_presence=False)
        return presence

    def _put_pending_presence_state(self, presence):
        res = super(WizEventAppendAssistant,
                    self)._put_pending_presence_state(presence)
        if self.contract:
            presence.contract = self.contract.id
        if self.employee:
            presence._update_employee_calendar_days(
                contract=self.contract, cancel_presence=False)
        return res
