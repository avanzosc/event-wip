# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import api, fields, models
from openerp.addons.event_track_assistant._common import _convert_to_local_date

date2str = fields.Date.to_string


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def button_validate_holiday(self):
        self.ensure_one()
        self.signal_workflow('validate')
        self._update_presences_validate_holiday()

    @api.multi
    def button_refuse_holiday(self):
        self.ensure_one()
        self._update_presences_refuse_holiday()
        self.signal_workflow('refuse')

    def _catch_employee_presences(self, holiday):
        presence_obj = self.env['event.track.presence']
        tz = self.env.user.tz
        date_from = date2str(_convert_to_local_date(holiday.date_from, tz=tz))
        date_to = date2str(_convert_to_local_date(holiday.date_to, tz=tz))
        cond = [('partner', '=',
                 holiday.employee_id.address_home_id.id),
                ('session_date_without_hour', '>=', date_from),
                ('session_date_without_hour', '<=', date_to)]
        presences = presence_obj.search(cond)
        return presences

    def _update_presences_validate_holiday(self):
        for holiday in self:
            if (holiday.employee_id.address_home_id and
                    holiday.type == 'remove'):
                absence_type = holiday.holiday_status_id
                presences = self._catch_employee_presences(holiday)
                if presences:
                    presences.write({'hr_holiday': holiday.id,
                                     'absence_type': absence_type.id})

    def _update_presences_refuse_holiday(self):
        for holiday in self:
            if (holiday.state == 'validate' and holiday.type == 'remove' and
                    holiday.employee_id.address_home_id):
                presences = self._catch_employee_presences(holiday)
                for presence in presences:
                    presence.write({'hr_holiday': False,
                                    'absence_type': False})
                    self._update_presence_absence_type(presence)

    def _update_presence_absence_type(self, presence):
        if presence.calendar_holiday_absence_type:
            presence.absence_type = (
                presence.calendar_holiday_absence_type.id)
        if presence.sale_contract_absence_type:
            presence.absence_type = (
                presence.sale_contract_absence_type.id)
