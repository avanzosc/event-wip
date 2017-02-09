# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _
from .._common import _convert_to_local_date, _convert_to_utc_date

datetime2str = fields.Datetime.to_string
date2str = fields.Date.to_string


class WizEventAppendAssistant(models.TransientModel):
    _name = 'wiz.event.append.assistant'

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

    @api.model
    def default_get(self, var_fields):
        tz = self.env.user.tz
        res = super(WizEventAppendAssistant, self).default_get(var_fields)
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

    @api.multi
    @api.onchange('from_date', 'to_date', 'partner')
    def onchange_dates_and_partner(self):
        self.ensure_one()
        res = {}
        from_date, to_date =\
            self._calc_dates_for_search_track(self.from_date, self.to_date)
        min_from_date = self._prepare_date_for_control(
            self.min_from_date, time=0.0)
        max_to_date = self._prepare_date_for_control(
            self.max_to_date, time=24.0)
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
        if from_date and to_date and self.partner:
            event_obj = self.env['event.event']
            for event in event_obj.browse(self.env.context.get('active_ids')):
                registrations = event.registration_ids.filtered(
                    lambda x: x.partner_id.id == self.partner.id and
                    x.state in ('done', 'open') and x.date_start and
                    x.date_end and
                    ((to_date >= x.date_start and to_date <= x.date_end) or
                     (from_date <= x.date_end and from_date >= x.date_start)))
                if registrations:
                    self.revert_dates()
                    return {'warning': {
                            'title': _('Error in dates'),
                            'message':
                            (_('You can not confirm this registration, because'
                               ' their dates overlap with another record of'
                               ' the same employee'))}}
        return res

    def revert_dates(self):
        tz = self.env.user.tz
        self.from_date = _convert_to_local_date(
            self.min_from_date, tz=tz).date()
        self.to_date = _convert_to_local_date(self.max_to_date, tz=tz).date()

    def _prepare_date_for_control(self, date, time=0.0):
        new_date = datetime2str(
            _convert_to_utc_date(date, time=time, tz=self.env.user.tz))
        return new_date

    @api.multi
    def action_append(self):
        self.ensure_one()
        event_obj = self.env['event.event']
        track_obj = self.env['event.track']
        if self.registration:
            self._update_registration_start_date(self.registration)
            self._update_registration_date_end(self.registration)
            self.registration.registration_open()
            cond = self._prepare_track_condition_search(
                self.registration.event_id)
            tracks = track_obj.search(cond)
            for track in tracks:
                presence = track.presences.filtered(
                    lambda x: x.session == track and
                    x.event == self.registration.event_id and
                    x.partner == self.partner)
                if presence:
                    self._put_pending_presence_state(presence)
                else:
                    self._create_presence_from_wizard(
                        track, self.registration.event_id)
            return self._exit_from_append_wizard()
        for event in event_obj.browse(self.env.context.get('active_ids')):
            registrations = event.registration_ids.filtered(
                lambda x: x.partner_id.id == self.partner.id and
                x.state == 'draft')
            if len(registrations) > 1:
                raise exceptions.Warning(
                    _('It has been found more than one registration in draft'
                      ' state for %s, in the event: %s')
                    % (self.partner.name, event.name))
            registration = self._update_create_registration(event,
                                                            registrations)
            registration.registration_open()
            cond = self._prepare_track_condition_search(event)
            tracks = track_obj.search(cond)
            for track in tracks:
                presence = track.presences.filtered(
                    lambda x: x.session == track and x.event == event and
                    x.partner == self.partner)
                if presence:
                    self._put_pending_presence_state(presence)
                else:
                    self._create_presence_from_wizard(track, event)
        return self._exit_from_append_wizard()

    def _update_create_registration(self, event, registrations):
        registration_obj = self.env['event.registration']
        if len(registrations) == 1:
            registration = registrations[0]
            self._update_registration_start_date(registration)
            self._update_registration_date_end(registration)
            registration.registration_open()
            registrations = registration.event_id.registration_ids.filtered(
                lambda x: x.id != registration.id and
                x.partner_id.id == self.partner.id and
                x.state in ('done', 'open') and x.date_start and
                x.date_end)
            for regis in registrations:
                if ((regis.date_end >= registration.date_start and
                     regis.date_end <= registration.date_end) or
                    (regis.date_start <= registration.date_end and
                     regis.date_start >= registration.date_start)):
                    self.from_date = self.min_from_date
                    self.to_date = self.max_to_date
                    raise exceptions.Warning(
                        _('You can not add employe to registration/event,'
                          'because the dates overlap in the event: %s,'
                          ' the registration: %s') % (regis.event_id.name,
                                                      regis.name))
        else:
            vals = self._prepare_registration_data(event)
            contact_id = self.partner.address_get().get('default', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                vals.update({'name': contact.name,
                             'email': contact.email,
                             'phone': contact.phone})
            registration = registration_obj.create(vals)
        return registration

    def _put_pending_presence_state(self, presence):
        presence.state = 'pending'

    def _prepare_track_condition_search(self, event):
        from_date, to_date = self._calc_dates_for_search_track(
            self.from_date, self.to_date)
        cond = [('id', 'in', event.track_ids.ids),
                ('date', '!=', False),
                ('date', '>=', from_date),
                ('date', '<=', to_date)]
        return cond

    def _update_registration_start_date(self, registration):
        reg_date_start = fields.Datetime.from_string(
            registration.date_start)
        wiz_from_date = fields.Date.from_string(self.from_date)
        if wiz_from_date != reg_date_start.date():
            registration.date_start = '{} {}'.format(
                self.from_date, reg_date_start.time())

    def _update_registration_date_end(self, registration):
        reg_date_end = fields.Datetime.from_string(
            registration.date_end)
        wiz_to_date = fields.Date.from_string(self.to_date)
        if wiz_to_date != reg_date_end.date():
            registration.date_end = '{} {}'.format(
                self.to_date, reg_date_end.time())

    def _prepare_registration_data(self, event):
        tz = self.env.user.tz
        date_start = datetime2str(_convert_to_utc_date(self.from_date, tz=tz))
        date_end = datetime2str(_convert_to_utc_date(self.to_date, tz=tz))
        vals = {
            'event_id': event.id,
            'partner_id': self.partner.id,
            'state': 'open',
            'date_start': event.date_begin if date_start < event.date_begin
            else date_start,
            'date_end': event.date_end if date_end < event.date_end
            else date_end,
        }
        return vals

    def _calc_dates_for_search_track(self, from_date, to_date):
        from_date = self._prepare_date_for_control(from_date, time=0.0)
        to_date = self._prepare_date_for_control(to_date, time=24.0)
        return from_date, to_date

    def _exit_from_append_wizard(self):
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

    def _local_date(self, ldate, time):
        event_obj = self.env['event.event']
        new_date = event_obj._convert_date_to_local_format(ldate).date()
        new_date = _convert_to_utc_date(
            new_date, time=time, tz=self.env.user.tz)
        return new_date

    def _create_presence_from_wizard(self, track, event):
        presence_obj = self.env['event.track.presence']
        vals = {'session': track.id,
                'event': event.id,
                'partner': self.partner.id}
        presence = presence_obj.create(vals)
        return presence
