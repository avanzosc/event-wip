# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_to_local_date, _convert_time_to_float

date2string = fields.Date.to_string
datetime2string = fields.Datetime.to_string
str2datetime = fields.Datetime.from_string


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    type_hour = fields.Many2one(
        comodel_name='hr.type.hour', string='Type hour')
    start_time = fields.Float(string='Start time', default=0.0)
    end_time = fields.Float(string='End time', default=0.0)

    @api.model
    def default_get(self, var_fields):
        tz = self.env.user.tz
        res = super(WizEventAppendAssistant, self).default_get(var_fields)
        res.update({
            'start_time': _convert_time_to_float(
                _convert_to_utc_date(res.get('min_from_date'), tz=tz), tz=tz),
            'end_time': _convert_time_to_float(
                _convert_to_utc_date(res.get('max_to_date'), tz=tz), tz=tz),
        })
        return res

    @api.multi
    @api.onchange('from_date', 'start_time', 'to_date', 'end_time', 'partner')
    def onchange_dates_and_partner(self):
        self.ensure_one()
        res = super(WizEventAppendAssistant, self).onchange_dates_and_partner()
        return res

    def revert_dates(self):
        tz = self.env.user.tz
        super(WizEventAppendAssistant, self).revert_dates()
        self.start_time = _convert_time_to_float(_convert_to_utc_date(
            self.min_from_date, tz=tz), tz=tz)
        self.end_time = _convert_time_to_float(_convert_to_utc_date(
            self.max_to_date, tz=tz), tz=tz)

    def _update_registration_start_date(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_start_date(
            registration)
        reg_date_start = str2datetime(registration.date_start)
        if self.start_time:
            wiz_from_date = _convert_to_utc_date(
                self.from_date, time=self.start_time, tz=self.env.user.tz)
            if wiz_from_date != reg_date_start:
                registration.date_start = wiz_from_date

    def _update_registration_date_end(self, registration):
        super(WizEventAppendAssistant, self)._update_registration_date_end(
            registration)
        reg_date_end = str2datetime(registration.date_end)
        if self.end_time:
            wiz_to_date = _convert_to_utc_date(
                self.to_date, time=self.end_time, tz=self.env.user.tz)
            if wiz_to_date != reg_date_end:
                registration.date_end = wiz_to_date

    def _prepare_registration_data(self, event):
        vals = super(WizEventAppendAssistant,
                     self)._prepare_registration_data(event)
        date_start = _convert_to_local_date(self.from_date).date()
        date_start = _convert_to_utc_date(
            date_start, time=self.start_time, tz=self.env.user.tz)
        date_end = _convert_to_local_date(self.to_date).date()
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
        super(WizEventAppendAssistant,
              self)._calc_dates_for_search_track(from_date, to_date)
        from_date = self._prepare_date_for_control(
            from_date, time=self.start_time or 0.0)
        to_date = self._prepare_date_for_control(
            to_date, time=self.end_time or 24.0)
        return from_date, to_date
