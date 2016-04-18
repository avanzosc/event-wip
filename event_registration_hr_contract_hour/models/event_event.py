# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class EventEvent(models.Model):
    _inherit = 'event.event'

    def _put_festives_in_sesions_from_sale_contract(self, calendars):
        super(EventEvent,
              self)._put_festives_in_sesions_from_sale_contract(calendars)
        type_hour_festive = self.env.ref(
            'sale_order_create_event_hour.type_hour_festive')
        for track in self.track_ids:
            for calendar in calendars:
                for day in calendar.lines:
                    track_month = fields.Datetime.from_string(
                        track.session_date).date().month
                    day_month = fields.Datetime.from_string(
                        day.date).date().month
                    track_day = fields.Datetime.from_string(
                        track.session_date).date().day
                    day_day = fields.Datetime.from_string(
                        day.date).date().day
                    if track_month == day_month and track_day == day_day:
                        if day.type_hour:
                            track.type_hour = day.type_hour.id
                        else:
                            track.type_hour = type_hour_festive.id
