# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestSaleOrderCreateEventHour(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestSaleOrderCreateEventHour, self).setUp()
        self.sunday = self.browse_ref(
            'sale_order_create_event_hour.type_hour_sunday')
        self.account.write({
            'start_time': 10.0,
            'end_time': 14.0,
        })
        self.project.write({
            'type_hour':
                self.ref('sale_order_create_event_hour.type_hour_working'),
        })

    def test_sale_order_sunday(self):
        self.sale_order.order_line.write({'sunday': True})
        self.sale_order.action_button_confirm()
        events = self.event_model.search(
            [('sale_order', '=', self.sale_order.id)])
        self.assertNotEquals(len(events), 0)
        self.assertNotEquals(len(events.mapped('track_ids')), 0)
        self.assertNotEquals(
            len(events.mapped('track_ids').filtered(
                lambda e: e.type_hour == self.sunday)), 0)

    def test_onchange_line_times(self):
        """Don't repeat this test."""
        pass

    def test_duplicate_sale_order(self):
        """Don't repeat this test."""
        pass
