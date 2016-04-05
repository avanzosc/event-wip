# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _update_presence_absence_type(self, presence):
        super(HrHolidays, self)._update_presence_absence_type(presence)
        if presence.type_hour.id > 2:
            presence.absence_type = False
            presence.partner_calendar_day.write({'absence_type': False,
                                                 'festive': False})

    def _update_calendar_days_from_presences(self, holiday, days):
        super(HrHolidays,
              self)._update_calendar_days_from_presences(holiday, days)
        for day in days:
            if day.festive_to_work:
                day.write({'absence_type': False,
                           'festive': False})
