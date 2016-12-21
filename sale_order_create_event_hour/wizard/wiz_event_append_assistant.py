# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_to_local_date, _convert_time_to_float
date2string = fields.Date.to_string
datetime2string = fields.Datetime.to_string


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    type_hour = fields.Many2one(
        comodel_name='hr.type.hour', string='Type hour')
    min_from_date = fields.Datetime(string='Min. from date', required=True)
    max_to_date = fields.Datetime(string='Max. to date', required=True)
    start_time = fields.Float(string='Start time', default=0.0)
    end_time = fields.Float(string='End time', default=0.0)

    @api.model
    def default_get(self, var_fields):
        tz = self.env.user.tz
        res = super(WizEventAppendAssistant, self).default_get(var_fields)
        from_date = False
        to_date = False
        for event in self.env['event.event'].browse(
                self.env.context.get('active_ids')):
            if not from_date or event.date_begin < from_date:
                new_date = _convert_to_local_date(
                    event.date_begin, tz=self.env.user.tz).date()
                res.update({'from_date': date2string(new_date),
                            'start_time':
                            _convert_time_to_float(event.date_begin, tz=tz),
                            'min_from_date': event.date_begin,
                            'min_event': event.id})
                from_date = self._prepare_date_for_control(new_date)
            if not to_date or event.date_end > to_date:
                new_date = _convert_to_local_date(
                    event.date_end, tz=tz).date()
                res.update({'to_date': date2string(new_date),
                            'end_time':
                            _convert_time_to_float(event.date_end, tz=tz),
                            'max_to_date': event.date_end,
                            'max_event': event.id})
                to_date = self._prepare_date_for_control(new_date)
        if res or (self.from_date and self.to_date):
            res = self._find_task_for_append_assistant(res)
        return res

    @api.multi
    @api.onchange('from_date', 'start_time', 'to_date', 'end_time', 'partner')
    def onchange_dates_and_partner(self):
        self.ensure_one()
        tz = self.env.user.tz
        event_obj = self.env['event.event']
        res = {}
        from_date = datetime2string(_convert_to_utc_date(
            self.from_date, self.start_time, tz=tz)) if self.from_date else\
            False
        to_date = datetime2string(_convert_to_utc_date(
            self.to_date, self.end_time, tz=tz)) if self.to_date else False
        if from_date and to_date and from_date > to_date:
            self._put_old_dates()
            return {'warning': {
                    'title': _('Error in from date'),
                    'message': (_('From date greater than date to'))}}
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
        if self.from_date and self.to_date and self.partner:
            for event in event_obj.browse(self.env.context.get('active_ids')):
                from_date = self._local_date(self.from_date, self.start_time)
                from_date = datetime2string(_convert_to_local_date(
                    str(from_date)[0:19], tz=tz).date())
                to_date = self._local_date(self.to_date, self.end_time)
                to_date = datetime2string(_convert_to_local_date(
                    str(to_date)[0:19], tz=tz).date())
                registrations = event.registration_ids.filtered(
                    lambda x: x.partner_id.id == self.partner.id and
                    x.state in ('done', 'open') and x.date_start and
                    x.date_end and
                    ((to_date >= x.date_start and to_date <= x.date_end) or
                     (from_date <= x.date_end and from_date >= x.date_start)))
                if registrations:
                    self.from_date = self.min_from_date
                    self.to_date = self.max_to_date
                    return {'warning': {
                            'title': _('Error in dates'),
                            'message':
                            (_('You can not confirm this registration, because'
                               ' their dates overlap with another record of'
                               ' the same employee'))}}
        res = self._find_task_for_append_assistant(res)
        if not res and not self.tasks:
            return {'warning': {
                    'title': _('Error in dates'),
                    'message': _('Not tasks found for introduced dates')}}
        return res

    def _put_old_dates(self):
        event_obj = self.env['event.event']
        self.from_date = event_obj._convert_date_to_local_format_with_hour(
            self.min_from_date).date()
        self.start_time = event_obj._convert_times_to_float(self.min_from_date)
        self.to_date = event_obj._convert_date_to_local_format_with_hour(
            self.max_to_date).date()
        self.end_time = event_obj._convert_times_to_float(self.max_to_date)

    def _prepare_tasks_search_condition(self, res):
        session_obj = self.env['event.track']
        tasks = self.env['project.task']
        if res.get('from_date', self.from_date) and res.get('to_date',
                                                            self.to_date):
            from_date = datetime2string(self._local_date(
                res.get('from_date', self.from_date),
                self.start_time))
            to_date = datetime2string(self._local_date(
                res.get('to_date', self.to_date),
                self.end_time))
            cond = [('event_id', 'in', self.env.context.get('active_ids')),
                    ('date', '>=', from_date),
                    ('date', '<=', to_date),
                    ('date', '!=', False)]
            sessions = session_obj.search(cond)
            tasks = sessions.mapped('tasks')
        return tasks

    def _update_registration_start_date(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_start_date(
            registration)
        event_date_start = registration.event_id.date_begin
        date_start = self._local_date(self.from_date, self.start_time)
        from_date = datetime2string(date_start)
        registration.date_start =\
            event_date_start if from_date < event_date_start else date_start

    def _compute_update_registration_start_date(self, registration):
        from_date = datetime2string(self._local_date(
            self.from_date, self.start_time))
        if from_date < registration.date_start:
            registration.date_start = from_date
            if from_date < registration.event_id.date_begin:
                registration.date_start = registration.event_id.date_begin

    def _update_registration_date_end(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_date_end(
            registration)
        event_date_end = registration.event_id.date_end
        date_end = self._local_date(self.to_date, self.end_time)
        to_date = datetime2string(date_end)
        registration.date_end =\
            event_date_end if to_date > event_date_end else date_end

    def _compute_update_registration_end_date(self, registration):
        to_date = datetime2string(self._local_date(
            self.to_date, self.end_time))
        if to_date > registration.date_end:
            registration.date_end = to_date
            if to_date > registration.event_id.date_end:
                registration.date_end = registration.event_id.date_end

    def _prepare_registration_data(self, event):
        vals = super(WizEventAppendAssistant,
                     self)._prepare_registration_data(event)
        date_start = event._convert_date_to_local_format(self.from_date).date()
        date_start = _convert_to_utc_date(
            date_start, time=self.start_time, tz=self.env.user.tz)
        date_end = event._convert_date_to_local_format(self.to_date).date()
        date_end = _convert_to_utc_date(
            date_end, time=self.end_time, tz=self.env.user.tz)
        vals.update({
            'date_start': event.date_begin
            if datetime2string(date_start) < event.date_begin else date_start,
            'date_end': event.date_end
            if datetime2string(date_end) > event.date_end else date_end,
        })
        return vals

    def _calc_dates_for_search_track(self, from_date, to_date):
        from_date = datetime2string(_convert_to_utc_date(
            from_date, time=self.start_time, tz=self.env.user.tz))
        to_date = datetime2string(_convert_to_utc_date(
            to_date, time=self.end_time, tz=self.env.user.tz))
        return from_date, to_date

    def _prepare_track_search_condition(self, event):
        cond = [('id', 'in', event.track_ids.ids),
                ('date', '=', False),
                ('date', '>=', self.from_date),
                ('date', '<=', self.to_date)]
        return cond
