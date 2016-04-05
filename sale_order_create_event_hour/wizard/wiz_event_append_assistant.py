# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _, exceptions


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
        event_obj = self.env['event.event']
        res = super(WizEventAppendAssistant, self).default_get(var_fields)
        from_date = False
        to_date = False
        for event in event_obj.browse(self.env.context.get('active_ids')):
            if not from_date or event.date_begin < from_date:
                new_date = event_obj._convert_date_to_local_format_with_hour(
                    event.date_begin).date()
                res.update({'from_date': new_date.strftime('%Y-%m-%d'),
                            'start_time':
                            event_obj._convert_times_to_float(
                                event.date_begin),
                            'min_from_date': event.date_begin,
                            'min_event': event.id})
                from_date = self._prepare_date_for_control(new_date)
            if not to_date or event.date_end > to_date:
                new_date = event_obj._convert_date_to_local_format_with_hour(
                    event.date_end).date()
                res.update({'to_date': new_date.strftime('%Y-%m-%d'),
                            'end_time':
                            event_obj._convert_times_to_float(event.date_end),
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
        event_obj = self.env['event.event']
        res = super
        if self.from_date and self.to_date:
            from_date = event_obj._put_utc_format_date(
                self.from_date, self.start_time).strftime("%Y-%m-%d %H:%M:%S")
            to_date = event_obj._put_utc_format_date(
                self.to_date, self.end_time).strftime("%Y-%m-%d %H:%M:%S")
            if from_date > to_date:
                self._put_old_dates()
                return {'warning': {
                        'title': _('Error in from date'),
                        'message':
                        (_('From date greater than date to'))}}
        if self.from_date:
            from_date = event_obj._put_utc_format_date(
                self.from_date, self.start_time).strftime("%Y-%m-%d %H:%M:%S")
            if from_date < self.min_from_date:
                self._put_old_dates()
                return {'warning': {
                        'title': _('Error in from date'),
                        'message':
                        (_('From date less than start date of the event %s') %
                         self.min_event.name)}}
        if self.to_date:
            to_date = event_obj._put_utc_format_date(
                self.to_date, self.end_time).strftime("%Y-%m-%d %H:%M:%S")
            if to_date > self.max_to_date:
                self._put_old_dates()
                return {'warning': {
                        'title': _('Error in to date'),
                        'message':
                        (_('From date greater than end date of the event %s') %
                         self.max_event.name)}}
        if self.from_date and self.to_date and self.partner:
            for event in event_obj.browse(self.env.context.get('active_ids')):
                from_date = self._local_date(self.from_date, self.start_time)
                from_date = event_obj._convert_date_to_local_format_with_hour(
                    str(from_date)[0:19]).date().strftime('%Y-%m-%d %H:%M:%S')
                to_date = self._local_date(self.to_date, self.end_time)
                to_date = event_obj._convert_date_to_local_format_with_hour(
                    str(to_date)[0:19]).date().strftime('%Y-%m-%d %H:%M:%S')
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
        if not res:
            if not self.tasks:
                return {'warning': {
                        'title': _('Error in dates'),
                        'message':
                        _('Not tasks found for introduced dates')}}
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
            from_date = self._local_date(
                res.get('from_date', self.from_date),
                self.start_time).strftime('%Y-%m-%d %H:%M:%S')
            to_date = self._local_date(
                res.get('to_date', self.to_date),
                self.end_time).strftime('%Y-%m-%d %H:%M:%S')
            cond = [('event_id', 'in', self.env.context.get('active_ids')),
                    ('date', '>=', from_date),
                    ('date', '<=', to_date),
                    ('date', '!=', False)]
            sessions = session_obj.search(cond)
            for session in sessions:
                for task in session.tasks:
                    if task not in tasks:
                        tasks += task
        return tasks

    def _update_registration_start_date(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_start_date(
            registration)
        registration.date_start = self._local_date(
            self.from_date, self.start_time)
        from_date = self._local_date(
            self.from_date, self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        if from_date < registration.event_id.date_begin:
            registration.date_start = registration.event_id.date_begin

    def _compute_update_registration_start_date(self, registration):
        from_date = self._local_date(
            self.from_date, self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        if from_date < registration.date_start:
            registration.date_start = from_date
            if from_date < registration.event_id.date_begin:
                registration.date_start = registration.event_id.date_begin

    def _update_registration_date_end(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_date_end(
            registration)
        registration.date_end = self._local_date(
            self.to_date, self.end_time)
        to_date = self._local_date(
            self.to_date, self.end_time).strftime('%Y-%m-%d %H:%M:%S')
        if to_date > registration.event_id.date_end:
            registration.date_end = registration.event_id.date_end

    def _compute_update_registration_end_date(self, registration):
        to_date = self._local_date(
            self.to_date, self.end_time).strftime('%Y-%m-%d %H:%M:%S')
        if to_date > registration.date_end:
            registration.date_end = to_date
            if to_date > registration.event_id.date_end:
                registration.date_end = registration.event_id.date_end

    def _prepare_registration_data(self, event):
        vals = super(WizEventAppendAssistant,
                     self)._prepare_registration_data(event)
        date_start = event._convert_date_to_local_format(self.from_date).date()
        date_end = event._convert_date_to_local_format(self.to_date).date()
        vals.update({'date_start': event._put_utc_format_date(date_start,
                                                              self.start_time),
                     'date_end': event._put_utc_format_date(date_end,
                                                            self.end_time)})
        date_start = event._put_utc_format_date(
            date_start, self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        if date_start < event.date_begin:
            vals['date_start'] = event.date_begin
        date_end = event._put_utc_format_date(
            date_end, self.end_time).strftime('%Y-%m-%d %H:%M:%S')
        if date_end > event.date_end:
            vals.update({'date_end': event.date_end})
        return vals

    def _calc_dates_for_search_track(self, from_date, to_date):
        event_obj = self.env['event.event']
        from_date = event_obj._put_utc_format_date(
            from_date, self.start_time).strftime('%Y-%m-%d %H:%M:%S')
        to_date = event_obj._put_utc_format_date(
            to_date, self.end_time).strftime('%Y-%m-%d %H:%M:%S')
        return from_date, to_date

    def _prepare_track_search_condition(self, event):
        cond = [('id', 'in', event.track_ids.ids),
                ('date', '=', False),
                ('date', '>=', self.from_date),
                ('date', '<=', self.to_date)]
        return cond
