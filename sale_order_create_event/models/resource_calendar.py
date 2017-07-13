# -*- coding: utf-8 -*-
# © 2017 Alfredo de la fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models
from openerp.addons.event_track_assistant._common import _convert_to_utc_date


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _calc_date_and_duration(self, date):
        lines = self.mapped('attendance_ids').filtered(
            lambda x: x.dayofweek == str(date.date().weekday()))
        if not lines:
            return False, False
        min_h = min(lines, key=lambda x: x.hour_from)
        new_date = _convert_to_utc_date(
            date, min_h.hour_from, tz=self.env.user.tz)
        duration = sum(x['hour_to'] - x['hour_from'] for x in lines)
        return new_date, duration
