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
        self.training_plan_model = self.env['training.plan']
        self.product_training_plan_model = self.env['product.training.plan']
        self.wizard_model = self.env['product.training.plan.wizard']
        vals = {
            'name': 'Test event track info',
            'planification': self.planification,
            'resolution': self.resolution,
            'html_info': self.html_info,
            'url': self.url,
        }
        cond = [('planification', '=', self.planification)]
        self.training_plan = self.training_plan_model.search(cond, limit=1)
        if not self.training_plan:
            self.training_plan = self.training_plan_model.create(vals)
        self.product_training_plan = self.product_training_plan_model.search([
            ('product_tmpl_id', '=', self.service_product.product_tmpl_id.id),
            ('product_id', '=', self.service_product.id),
            ('sequence', '=', 1),
            ('training_plan_id', '=', self.training_plan.id),
        ], limit=1)
        if not self.product_training_plan:
            vals = {
                'product_tmpl_id': self.service_product.product_tmpl_id.id,
                'product_id': self.service_product.id,
                'sequence': 1,
                'training_plan_id': self.training_plan.id}
            self.product_training_plan = (
                self.product_training_plan_model.create(vals))
        self.product_training_plan = self.product_training_plan_model.search([
            ('product_tmpl_id', '=', self.service_product.product_tmpl_id.id),
            ('product_id', '=', False),
            ('sequence', '=', 1),
            ('training_plan_id', '=', self.training_plan.id),
        ], limit=1)
        if not self.product_training_plan:
            vals = {
                'product_tmpl_id': self.service_product.product_tmpl_id.id,
                'sequence': 1,
                'training_plan_id': self.training_plan.id}
            self.product_training_plan = (
                self.product_training_plan_model.create(vals))

    def test_sale_order_create_event(self):
        """Don't repeat this test."""
        pass

    def test_sale_order_create_event_by_task(self):
        super(TestTrackInfo, self).test_sale_order_create_event_by_task()
        cond = [('sale_order_line', '=', self.sale_order.order_line[0].id)]
        event = self.event_model.search(cond, limit=1)
        self.assertEquals(self.sale_order.order_line[0].event_id, event)
        for line in self.sale_order.order_line:
            track = line.event_id.track_ids[
                self.product_training_plan.sequence - 1]
            self.assertIn(self.url, track.url)
            self.assertIn(self.planification, track.planification)
            self.assertIn(self.resolution, track.resolution)
            self.assertIn(
                u"<p>{}".format(self.html_info), track.description)

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

    def test_product_training_plan_wizard(self):
        super(TestTrackInfo, self).test_sale_order_create_event_by_task()
        cond = [('sale_order_line', '=', self.sale_order.order_line[0].id)]
        event = self.event_model.search(cond, limit=1)
        event.track_ids.write({'url': '',
                               'planification': '',
                               'resolution': '',
                               'description': ''})
        wiz = self.wizard_model.create({'product_id': self.service_product.id})
        wiz.with_context(active_id=event.id).put_training_plan_in_sessions()
        self.assertIn(
            'www.example.com', event.track_ids[0].url, 'Bad event track URL')
        self.assertIn(
            'This is the planification', event.track_ids[0].planification,
            'Bad event track planification')
        self.assertIn(
            'This is the resolution', event.track_ids[0].resolution,
            'Bad event track resolution')
        self.assertIn(
            '<p>This is the html_info</p>', event.track_ids[0].description,
            'Bad event track description')
