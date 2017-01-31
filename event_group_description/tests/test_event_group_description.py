# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestEventGroupDescription(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestEventGroupDescription, self).setUp()
        for line in self.sale_order.mapped('order_line').filtered(
                lambda l: l.product_id.recurring_service):
            line.courses = 'Courses test for description'
        self.sale_order.order_line.write({
            'monday': True,
            'wednesday': True,
            'friday': True,
            'saturday': True,
            'sunday': True,
        })

    def test_sale_order_create_event_by_task(self):
        super(TestEventGroupDescription,
              self).test_sale_order_create_event_by_task()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertEquals(
            sum(events.mapped('count_sale_lines')),
            len(self.sale_order.order_line))
        for event in events.filtered('sale_order_line'):
            result = event.show_sale_lines()
            domain = result.get('domain')
            self.assertIn(
                domain[0][2], self.sale_order.mapped('order_line').ids)

    def test_sale_order_confirm(self):
        """Don't repeat this test."""
        pass

    def test_onchange_line_times(self):
        """Don't repeat this test."""
        pass

    def test_change_session_date(self):
        """Don't repeat this test."""
        pass

    def test_event_track_registration_open_button(self):
        """Don't repeat this test."""
        pass

    def test_event_track_assistant_delete(self):
        """Don't repeat this test."""
        pass

    def test_event_track_assistant_delete_from_event(self):
        """Don't repeat this test."""
        pass

    def test_event_assistant_track_assistant_confirm_assistant(self):
        """Don't repeat this test."""
        pass

    def test_duplicate_sale_order(self):
        """Don't repeat this test."""
        pass
