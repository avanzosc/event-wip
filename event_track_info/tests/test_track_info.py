# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event import TestSaleOrderCreateEvent


class TestTrackInfo(TestSaleOrderCreateEvent):

    def setUp(self):
        super(TestTrackInfo, self).setUp()
        self.url = 'www.example.com'
        self.planification = 'This is the planification'
        self.resolution = 'This is the resolution'
        self.html_info = 'This is the html_info'
        self.track_template = self.env['product.event.track.template'].create({
            'product_id': self.service_product.id,
            'sequence': 0,
            'planification': self.planification,
            'resolution': self.resolution,
            'html_info': self.html_info,
            'url': self.url,
        })

    def test_sale_order_confirm(self):
        self.sale_order.action_button_confirm()
        for track in self.sale_order.mapped('order_line.event_id.track_ids'):
            self.assertEquals(track.url, self.url)
            self.assertEquals(track.planification, self.planification)
            self.assertEquals(track.resolution, self.resolution)
            self.assertEquals(track.html_info, self.html_info)
