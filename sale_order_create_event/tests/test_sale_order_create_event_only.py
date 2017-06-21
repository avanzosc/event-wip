# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields
from .common import SaleOrderCreateEventSetup

str2date = fields.Date.from_string


class TestSaleOrderCreateEventOnly(SaleOrderCreateEventSetup):

    def setUp(self):
        super(TestSaleOrderCreateEventOnly, self).setUp()

    def test_change_session_date(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        wiz_vals = {'days': 35}
        wiz = self.change_date_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': [event.track_ids[len(
                event.track_ids)-1].id]}).change_session_date()
        self.assertEqual(
            str2date(event.track_ids[len(
                event.track_ids)-1].date), str2date(event.date_end),
            'Session and event with different end date')
        wiz_vals = {'days': -28}
        wiz = self.change_date_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': [event.track_ids[0].id]}).change_session_date()
        self.assertEqual(
            str2date(event.track_ids[0].date), str2date(event.date_begin),
            'Session and event with different start date')

    def test_duplicate_sale_order(self):
        self.sale_order.project_by_task = 'yes'
        self.sale_order.action_button_confirm()
        self.assertTrue(self.sale_order.mapped('order_line.event_id'))
        copy_sale_order = self.sale_order.copy()
        self.assertEquals(copy_sale_order.state, 'draft')
        self.assertFalse(copy_sale_order.mapped('order_line.event_id'))
