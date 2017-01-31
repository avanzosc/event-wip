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

    def test_sale_order_create_event(self):
        """Don't repeat this test."""
        pass

    def test_sale_order_create_event_by_task(self):
        super(TestTrackInfo, self).test_sale_order_create_event_by_task()
        cond = [('sale_order_line', '=', self.sale_order.order_line[0].id)]
        event = self.event_model.search(cond, limit=1)
        self.assertEquals(self.sale_order.order_line[0].event_id, event)
        for line in self.sale_order.order_line:
            track = line.event_id.track_ids[self.track_template.sequence - 1]
            self.assertEquals(track.url, self.url)
            self.assertEquals(track.planification, self.planification)
            self.assertEquals(track.resolution, self.resolution)
            self.assertEquals(
                track.description, u"<p>{}</p>".format(self.html_info))

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
