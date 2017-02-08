# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_time_to_float


class WizEventDeleteAssistant(models.TransientModel):
    _inherit = 'wiz.event.delete.assistant'

    min_from_date = fields.Datetime(string='Min. from date', required=True)
    max_to_date = fields.Datetime(string='Max. to date', required=True)
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
        self.start_time = _convert_time_to_float(self.min_from_date, tz=tz)
        self.end_time = _convert_time_to_float(self.max_to_date, tz=tz)
