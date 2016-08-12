# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestTrackInfo(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestTrackInfo, self).setUp()
        self.event_model = self.env['event.event']
        self.url = 'www.example.com'
        self.planification = 'This is the planification'
        self.resolution = 'This is the resolution'
        self.html_info = 'This is the html_info'
        self.track_template = self.env['product.event.track.template'].create({
            'product_id': self.service_product.id,
            'sequence': 0,
            'name': 'Session 1',
            'planification': self.planification,
            'resolution': self.resolution,
            'html_info': self.html_info,
            'url': self.url,
        })

    def test_sale_order_confirm(self):
        self.sale_order2.action_button_confirm()
        cond = [('sale_order_line', '=', self.sale_order2.order_line[0].id)]
        event = self.event_model.search(cond, limit=1)
        self.sale_order2.order_line[0].event_id = event.id
        self.sale_order2.action_button_confirm()
        for track in self.sale_order2.mapped('order_line.event_id.track_ids'):
            if track.url:
                self.assertEquals(track.url, self.url)
            if track.planification:
                self.assertEquals(track.planification, self.planification)
            if track.resolution:
                self.assertEquals(track.resolution, self.resolution)
