# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _
from .._common import _convert_to_local_date, _convert_to_utc_date

datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class WizEventDeleteAssistant(models.TransientModel):
    _name = 'wiz.event.delete.assistant'

    from_date = fields.Date(string='From date')
    to_date = fields.Date(string='To date')
    registration = fields.Many2one(
        comodel_name='event.registration', string='Partner registration')
    partner = fields.Many2one(comodel_name='res.partner', string='Partner')
    min_event = fields.Many2one(
        comodel_name='event.event', string='Min. event')
    min_from_date = fields.Date(string='Min. from date')
    max_event = fields.Many2one(
        comodel_name='event.event', string='Max. event')
    max_to_date = fields.Date(string='Max. to date')
    past_sessions = fields.Boolean(string='Past Sessions')
    later_sessions = fields.Boolean(string='Later Sessions')
    message = fields.Char(string='Message', readonly=True)
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
                'from_date': from_date.date(),
                'to_date': to_date.date(),
                'min_from_date': from_date,
                'max_to_date': to_date,
                'min_event': min_event.id,
                'max_event': max_event.id,
            })
        return res

    @api.onchange('from_date', 'to_date', 'partner')
    def onchange_information(self):
        event_track_obj = self.env['event.track']
        self.past_sessions = False
        self.later_sessions = False
        self.message = ''
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
    def _dates_control(self):
        self.ensure_one()
        res = {}
        from_date, to_date =\
            self._prepare_dates_for_search_registrations()
        if from_date and to_date and from_date > to_date:
            self._put_old_dates()
            return {'warning': {
                    'title': _('Error in from date'),
                    'message':
                    (_('From date greater than date to'))}}
        if from_date and from_date < self.min_from_date:
            self._put_old_dates()
            return {'warning': {
                    'title': _('Error in from date'),
                    'message':
                    (_('From date less than start date of the event %s') %
                     self.min_event.name)}}
        if to_date and to_date > self.max_to_date:
            self._put_old_dates()
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

    @api.multi
    def action_delete_past_and_later(self):
        self.ensure_one()
        if not self.removal_date:
            raise exceptions.Warning(_('You must enter the removal date'))
        if not self.notes:
            raise exceptions.Warning(_('You must enter the notes'))
        self.action_delete()

    @api.multi
    def action_nodelete_past_and_later(self):
        self.ensure_one()
        event_obj = self.env['event.event']
        presence_obj = self.env['event.track.presence']
        event_ids = self.registration.event_id.ids if self.registration else\
            self.env.context.get('active_ids', [])
        for event in event_obj.browse(event_ids):
            sessions = self.partner.session_ids.filtered(
                lambda x: x.event_id == event)
            self._delete_registrations_between_dates(sessions)
            registrations = event.registration_ids.filtered(
                lambda x: x.partner_id == self.partner and
                x.state == 'open') if not self.registration else\
                self.registration
            from_date, to_date = self._prepare_dates_for_search_registrations()
            for registration in registrations:
                cond = [('event', '=', event.id),
                        ('partner', '=', self.partner.id),
                        ('state', '!=', 'cancel'),
                        ('session_date', '>=', registration.date_start),
                        ('session_date', '<=', registration.date_end), '|',
                        ('session_date', '<', from_date),
                        ('session_date', '>', to_date)]
                presences = presence_obj.search(cond, limit=1)
                if not presences:
                    registration.button_reg_cancel()
        return self._open_event_tree_form()

    def _prepare_dates_for_search_registrations(self):
        from_date = self._prepare_date_for_control(self.from_date)
        to_date = self._prepare_date_for_control(self.to_date)
        return from_date, to_date

    def _put_old_dates(self):
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
        if self.registration:
            cond = [('event', '=', self.registration.event_id.id),
                    ('session_date', '>=', self.registration.date_start),
                    ('session_date', '<=', self.registration.date_end)]
        else:
            cond = [('event', 'in', self.env.context.get('active_ids'))]
        cond.append(('partner', '=', self.partner.id))
        presences = self.env['event.track.presence'].search(cond)
        presences.button_canceled()
        return presences

    def _delete_registrations_between_dates(self, sessions):
        event_track_obj = self.env['event.track']
        cond = self._prepare_track_search_condition_for_delete(sessions)
        tracks = event_track_obj.search(cond)
        presences = tracks.mapped('presences').filtered(
            lambda x: x.partner == self.partner)
        presences.button_canceled()

    def _prepare_track_search_condition_for_delete(self, sessions):
        from_date, to_date = self._prepare_dates_for_search_registrations()
        cond = [('id', 'in', sessions.ids),
                ('date', '!=', False),
                ('date', '>=', from_date),
                ('date', '<=', to_date)]
        return cond

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
