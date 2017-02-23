# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_time_to_float

str2datetime = fields.Datetime.from_string


class WizEventDeleteAssistant(models.TransientModel):
    _inherit = 'wiz.event.delete.assistant'

    start_time = fields.Float(string='Start time', default=0.0)
    end_time = fields.Float(string='End time', default=0.0)

    @api.model
    def default_get(self, var_fields):
        tz = self.env.user.tz
        res = super(WizEventDeleteAssistant, self).default_get(var_fields)
        res.update({
            'start_time': _convert_time_to_float(
                _convert_to_utc_date(res.get('min_from_date'), tz=tz), tz=tz),
            'end_time': _convert_time_to_float(
                _convert_to_utc_date(res.get('max_to_date'), tz=tz), tz=tz),
        })
        return res

    def _prepare_dates_for_search_registrations(self):
        super(WizEventDeleteAssistant,
              self)._prepare_dates_for_search_registrations()
        from_date = self._prepare_date_for_control(
            self.from_date, self.start_time)
        to_date = self._prepare_date_for_control(
            self.to_date, self.end_time)
        return from_date, to_date

    def revert_dates(self):
        tz = self.env.user.tz
        super(WizEventDeleteAssistant, self).revert_dates()
        self.start_time = _convert_time_to_float(_convert_to_utc_date(
            self.min_from_date, tz=tz), tz=tz)
        self.end_time = _convert_time_to_float(_convert_to_utc_date(
            self.max_to_date, tz=tz), tz=tz)

    def _update_registration_date_end(self, registration):
        super(WizEventDeleteAssistant, self)._update_registration_date_end(
            registration)
        reg_date_end = str2datetime(registration.date_end)
        wiz_from_date = _convert_to_utc_date(
            self.from_date, time=self.start_time, tz=self.env.user.tz)
        if wiz_from_date != reg_date_end:
            registration.date_end = wiz_from_date
