# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def _calculate_counts(self):
        events = self.env['event.event']
        sessions = self.env['event.track']
        for contract in self:
            contract.calendar_day_count = len(contract.calendar_days)
            contract.registration_count = len(contract.registrations)
            for registration in contract.registrations:
                events += registration.event_id
            contract.event_count = len(events)
            contract.presence_count = len(contract.presences)
            for presence in contract.presences:
                sessions += presence.session
            contract.session_count = len(sessions)

    registrations = fields.One2many(
        comodel_name='event.registration', inverse_name='contract',
        string='Registrations')
    presences = fields.One2many(
        comodel_name='event.track.presence', inverse_name='contract',
        string='Presences to sessions')
    calendar_day_count = fields.Integer(
        string='Employee calendar days', compute='_calculate_counts')
    event_count = fields.Integer(
        string='Events counter', compute='_calculate_counts')
    registration_count = fields.Integer(
        string='Registrations counter', compute='_calculate_counts')
    session_count = fields.Integer(
        string='Sessions counter', compute='_calculate_counts')
    presence_count = fields.Integer(
        string='Presences counter', compute='_calculate_counts')

    def _search_contracts_without_date_end(self, partner, to_date):
        cond = [('partner', '=', partner.id),
                ('date_start', '<=', to_date),
                ('date_end', '=', False)]
        return cond

    def _search_contracts_with_date_end(self, partner, from_date, to_date):
        cond = [('partner', '=', partner.id),
                ('date_start', '<=', to_date),
                ('date_end', '!=', False),
                ('date_end', '>=', from_date)]
        return cond

    @api.multi
    def show_contract_calendar_days(self):
        res = {'view_mode': 'calendar,tree,form',
               'res_model': 'res.partner.calendar.day',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', self.calendar_days.ids)]}
        return res

    @api.multi
    def show_contract_events(self):
        events = self.env['event.event']
        for registration in self.registrations:
            events += registration.event_id
        res = {'view_mode': 'kanban,calendar,tree,form',
               'res_model': 'event.event',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', events.ids)]}
        return res

    @api.multi
    def show_contract_registrations(self):
        res = {'view_mode': 'tree,form,calendar,graph',
               'res_model': 'event.registration',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', self.registrations.ids)]}
        return res

    @api.multi
    def show_contract_sessions(self):
        sessions = self.env['event.track']
        for presence in self.presences:
            sessions += presence.session
        res = {'view_mode': 'tree,form,calendar',
               'res_model': 'event.track',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', sessions.ids)]}
        return res

    @api.multi
    def show_contract_presences(self):
        res = {'view_mode': 'tree,form',
               'res_model': 'event.track.presence',
               'view_id': False,
               'type': 'ir.actions.act_window',
               'view_type': 'form',
               'domain': [('id', 'in', self.presences.ids)]}
        return res
