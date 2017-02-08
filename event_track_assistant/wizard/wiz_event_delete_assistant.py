# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
from .._common import _convert_to_local_date, _convert_to_utc_date

datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class WizEventDeleteAssistant(models.TransientModel):
    _name = 'wiz.event.delete.assistant'

    from_date = fields.Date(string='From date', required=True)
    to_date = fields.Date(string='To date', required=True)
    registration = fields.Many2one(
        comodel_name='event.registration', string='Partner registration')
    partner = fields.Many2one(
        comodel_name='res.partner', string='Partner', required=True)
    min_event = fields.Many2one(
        comodel_name='event.event', string='Min. event')
    min_from_date = fields.Date(string='Min. from date')
    max_event = fields.Many2one(
        comodel_name='event.event', string='Max. event')
    max_to_date = fields.Date(string='Max. to date')
    past_sessions = fields.Boolean(
        string='Past Sessions', compute='_compute_past_later_sessions')
    later_sessions = fields.Boolean(
        string='Later Sessions', compute='_compute_past_later_sessions')
    message = fields.Char(
        string='Message', readonly=True,
        compute='_compute_past_later_sessions')
    notes = fields.Text(string='Notes')
    removal_date = fields.Date(
        string='Removal date',
        default=lambda self: fields.Date.context_today(self))

    @api.model
    def default_get(self, var_fields):
        tz = self.env.user.tz
        res = super(WizEventDeleteAssistant, self).default_get(var_fields)
        events = self.env['event.event'].browse(
            self.env.context.get('active_ids'))
        if events:
            from_date = _convert_to_local_date(
                min(events.mapped('date_begin')), tz)
            to_date = _convert_to_local_date(
                max(events.mapped('date_end')), tz)
            min_event = events.sorted(key=lambda e: e.date_begin)[:1]
            max_event = events.sorted(key=lambda e: e.date_end,
                                      reverse=True)[:1]
            res.update({
                'from_date': date2str(from_date.date()),
                'to_date': date2str(to_date.date()),
                'min_from_date': datetime2str(from_date),
                'max_to_date': datetime2str(to_date),
                'min_event': min_event.id,
                'max_event': max_event.id,
            })
        return res

    @api.depends('from_date', 'to_date', 'partner')
    def _compute_past_later_sessions(self):
        event_track_obj = self.env['event.track']
        if self.from_date and self.to_date and self.partner:
            if self.registration:
                sessions = self.partner.session_ids.filtered(
                    lambda x: x.event_id.id == self.registration.event_id.id)
                from_date, to_date =\
                    self._prepare_dates_for_search_registrations()
                self.past_sessions = self.registration.date_start != from_date
                self.later_sessions = self.registration.date_end != to_date
            else:
                sessions = self.partner.session_ids.filtered(
                    lambda x: x.event_id.id in
                    self.env.context.get('active_ids'))
                cond = self._prepare_track_condition_from_date(sessions)
                prev = event_track_obj.search(cond, limit=1)
                if prev:
                    self.past_sessions = True
                cond = self._prepare_track_condition_to_date(sessions)
                later = event_track_obj.search(cond, limit=1)
                if later:
                    self.later_sessions = True
            if self.past_sessions and self.later_sessions:
                self.message = _('This person has sessions with dates before'
                                 ' and after')
            elif self.past_sessions:
                self.message = _('This person has sessions with dates before')
            elif self.later_sessions:
                self.message = _('This person has sessions with dates after')

    @api.multi
    @api.onchange('from_date', 'to_date')
    def onchange_dates(self):
        self.ensure_one()
        res = {}
        from_date, to_date =\
            self._prepare_dates_for_search_registrations()
        min_from_date = self._prepare_date_for_control(self.min_from_date)
        max_to_date = self._prepare_date_for_control(self.max_to_date)
        if from_date and to_date and from_date > to_date:
            self.revert_dates()
            return {'warning': {
                    'title': _('Error in from date'),
                    'message': (_('From date greater than date to'))}}
        if from_date and from_date < min_from_date:
            self.revert_dates()
            return {'warning': {
                    'title': _('Error in from date'),
                    'message':
                    (_('From date less than start date of the event %s') %
                     self.min_event.name)}}
        if to_date and to_date > max_to_date:
            self.revert_dates()
            return {'warning': {
                    'title': _('Error in to date'),
                    'message':
                    (_('From date greater than end date of the event %s') %
                     self.max_event.name)}}
        return res

    def _prepare_date_for_control(self, date, time=0.0):
        new_date = datetime2str(
            _convert_to_utc_date(date, time=time, tz=self.env.user.tz))
        return new_date

    def _prepare_track_condition_from_date(self, sessions):
        from_date, to_date = self._prepare_dates_for_search_registrations()
        cond = [('id', 'in', sessions.ids),
                ('date', '!=', False),
                ('date', '<', from_date)]
        return cond

    def _prepare_track_condition_to_date(self, sessions):
        from_date, to_date = self._prepare_dates_for_search_registrations()
        cond = [('id', 'in', sessions.ids),
                ('date', '!=', False),
                ('date', '>', to_date)]
        return cond

    @api.multi
    def action_delete(self):
        self.ensure_one()
        self._cancel_registration()
        self._cancel_presences()
        return self._open_event_tree_form()

    def _prepare_dates_for_search_registrations(self):
        from_date = self._prepare_date_for_control(self.from_date)
        to_date = self._prepare_date_for_control(self.to_date)
        return from_date, to_date

    def revert_dates(self):
        tz = self.env.user.tz
        self.from_date = _convert_to_local_date(
            self.min_from_date, tz=tz).date()
        self.to_date = _convert_to_local_date(self.max_to_date, tz=tz).date()

    def _cancel_registration(self):
        cond = [('event_id', 'in', self.env.context.get('active_ids')),
                ('partner_id', '=', self.partner.id),
                ('state', '=', 'open')]
        registrations = self.env['event.registration'].search(cond)\
            if not self.registration else self.registration
        if self.removal_date and self.notes:
            registrations.write({'removal_date': self.removal_date,
                                 'notes': self.notes})
        for registration in registrations:
            registration.button_reg_cancel()
        return registrations

    def _cancel_presences(self):
        from_date, to_date = self._prepare_dates_for_search_registrations()
        cond = [('event', 'in', self.env.context.get('active_ids')),
                ('state', '=', 'pending'),
                ('partner', '=', self.partner.id),
                ('session_date', '>=', from_date),
                ('session_date', '<=', to_date)]
        presences = self.env['event.track.presence'].search(cond)
        presences.button_canceled()
        return presences

    def _open_event_tree_form(self):
        active_ids = self.env.context.get('active_ids', [])
        view_mode = 'kanban,calendar,tree,form' if len(active_ids) > 1 else\
            'form,kanban,calendar,tree'
        result = {'name': _('Event'),
                  'type': 'ir.actions.act_window',
                  'res_model': 'event.event',
                  'view_type': 'form',
                  'view_mode': view_mode,
                  'res_id': active_ids[0],
                  'target': 'current',
                  'context': self.env.context}
        return result
