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

    def test_event_group_description(self):
        self.sale_order.order_line.write({
            'monday': True,
            'wednesday': True,
            'friday': True,
            'saturday': True,
            'sunday': True,
        })
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEquals(
            len([events]), 0, 'Sale order without event')
        self.assertEquals(
            sum(events.mapped('count_sale_lines')), 0)

    def test_event_group_description_by_task(self):
        self.sale_order.project_by_task = 'yes'
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEquals(
            len([events]), 0, 'Sale order without event')
        self.assertEquals(
            sum(events.mapped('count_sale_lines')),
            len(self.sale_order.order_line))
        for event in events.filtered('sale_order_line'):
            result = event.show_sale_lines()
            domain = result.get('domain')
            self.assertIn(
                domain[0][2], self.sale_order.mapped('order_line').ids)
