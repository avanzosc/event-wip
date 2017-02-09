# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models
from openerp.addons.event_track_assistant._common import _convert_to_local_date


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    def _put_init_dates_in_wizard(self):
        tz = self.env.user.tz
        if not self.from_date:
            self.from_date = _convert_to_local_date(
                self.min_from_date, tz=tz).date()
        if not self.to_date:
            self.to_date = _convert_to_local_date(
                self.max_to_date, tz=tz).date()

    def _put_pending_presence_state(self, presence):
        res = super(WizEventAppendAssistant, self)._put_pending_presence_state(
            presence)
        self._update_presence_type_hour(presence)
        return res

    def _create_presence_from_wizard(self, track, event):
        presence = super(WizEventAppendAssistant,
                         self)._create_presence_from_wizard(track, event)
        self._update_presence_type_hour(presence)
        return presence

    def _update_presence_type_hour(self, presence):
        if presence.session.type_hour:
            type_hour_working = self.env.ref(
                'sale_order_create_event_hour.type_hour_working')
            type_hour_festive = self.env.ref(
                'sale_order_create_event_hour.type_hour_festive')
            partner_calendar_day = presence.partner_calendar_day
            if (presence.session.type_hour.id == type_hour_working.id and
                    partner_calendar_day.calendar_holiday_day):
                if partner_calendar_day.calendar_holiday_day.type_hour:
                    presence.type_hour = (
                        partner_calendar_day.calendar_holiday_day.type_hour.id)
                else:
                    presence.type_hour = type_hour_festive.id
            else:
                presence.type_hour = presence.session.type_hour.id
        else:
            if self.type_hour:
                presence.type_hour = self.type_hour.id
        if presence.type_hour.id > 2:
            presence.absence_type = False
            presence.partner_calendar_day.write({'absence_type': False,
                                                 'festive': False,
                                                 'festive_to_work': True})
