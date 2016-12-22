# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestEventCalendarHoliday(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestEventCalendarHoliday, self).setUp()
        self.holiday_model = self.env['calendar.holiday']
        self.absence_id = self.ref('hr_holidays.holiday_status_comp')
        calendar_line_vals = {
            'date': '2015-02-25',
            'absence_type': self.absence_id}
        calendar_vals = {'name': 'Holidays calendar',
                         'lines': [(0, 0, calendar_line_vals)]}
        self.calendar_holiday = self.holiday_model.create(calendar_vals)
        self.account.festive_calendars = [(6, 0, [self.calendar_holiday.id])]

    def test_event_calendar_holiday(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        tracks = events.mapped('track_ids').filtered(
            lambda x: x.absence_type.id == self.absence_id)
        self.assertNotEqual(
            len(tracks), 0, 'Sessions no generated with absence type')
