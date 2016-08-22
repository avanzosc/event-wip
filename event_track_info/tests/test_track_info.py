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
        track_tmpl_model = self.env['product.event.track.template']
        vals = {
            'planification': self.planification,
            'resolution': self.resolution,
            'html_info': self.html_info,
            'url': self.url,
        }
        self.track_template = track_tmpl_model.search([
            ('product_id', '=', self.service_product.id),
            ('sequence', '=', 1),
        ], limit=1)
        if self.track_template:
            self.track_template.write(vals)
        else:
            vals.update({
                'product_id': self.service_product.id,
                'sequence': 1,
                'name': 'Test Template',
            })
            self.track_template = track_tmpl_model.create(vals)

    def test_sale_order_confirm_track_info(self):
        self.sale_order.write({
            'project_by_task': 'yes',
        })
        self.sale_order.action_button_confirm()
        cond = [('sale_order_line', '=', self.sale_order.order_line[0].id)]
        event = self.event_model.search(cond, limit=1)
        # This must be checked, it should have assigned the event to the line
        self.sale_order.order_line[0].event_id = event.id
        self.sale_order.action_button_confirm()
        for line in self.sale_order.order_line:
            track = line.event_id.track_ids[self.track_template.sequence - 1]
            self.assertEquals(track.url, self.url)
            self.assertEquals(track.planification, self.planification)
            self.assertEquals(track.resolution, self.resolution)
            self.assertEquals(
                track.description, u"<p>{}</p>".format(self.html_info))
