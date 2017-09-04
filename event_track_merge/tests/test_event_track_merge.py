# -*- coding: utf-8 -*-
# Copyright 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventTrackMerge(common.TransactionCase):

    def setUp(self):
        super(TestEventTrackMerge, self).setUp()
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.event_model = self.env['event.event']
        self.partner_model = self.env['res.partner']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.wiz_merge_model = self.env['wiz.event.track.merge']
        self.env.user.write({'tz': u'UTC'})
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2025-12-01',
                        'date': '2025-12-15',
                        'use_tasks': True}
        self.account = self.account_model.create(account_vals)
        self.project = self.env['project.project'].search(
            [('analytic_account_id', '=', self.account.id)], limit=1)[:1]
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        self.service_product.write({
            'performance': 5.0,
            'recurring_service': True,
            'route_ids':
            [(6, 0,
              [self.ref('procurement_service_project.route_serv_project')])],
            'ticket_event_product_ids':
            [(6, 0,
              [self.ref('event_sale.product_product_event')])],
        })
        sale_vals = {
            'name': 'sale order 1',
            'partner_id': self.ref('base.res_partner_1'),
            'project_id': self.account.id,
            'project_by_task': 'no',
        }
        sale_line_vals = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price,
            'performance': self.service_product.performance,
            'december': True,
            'week1': True,
            'monday': True,
            'start_date': '2025-12-01',
            'start_hour': 8.00,
            'end_date': '2025-12-07',
            'end_hour': 09.00}
        sale_line_vals2 = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price,
            'performance': self.service_product.performance,
            'december': True,
            'week1': True,
            'monday': True,
            'start_date': '2025-12-01',
            'start_hour': 8.00,
            'end_date': '2025-12-07',
            'end_hour': 09.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals),
                                   (0, 0, sale_line_vals2)]
        self.sale_order = self.sale_model.create(sale_vals)
        self.partner = self.partner_model.create({
            'name': 'Test event_track_merge Partner',
        })

    def test_event_track_merge(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        add_wiz = self.wiz_add_model.with_context(
            active_ids=event.ids).create(
            {'partner': self.partner.id,
             'from_date': event.date_begin,
             'min_from_date': event.date_begin,
             'max_to_date': event.date_end,
             'to_date': event.date_end})
        add_wiz.action_append()
        merge_wiz = self.wiz_merge_model.with_context(
            active_ids=event.ids).create(
            {'name': 'merge event sessions'})
        merge_wiz.with_context(
            active_ids=event.ids).buttom_merge_event_tracks()
        self.assertEquals(len(event.track_ids), 1,
                          'No unique session in event')
        self.assertEquals(event.count_tasks, 1,
                          'No unique task in event')
        self.assertEquals(event.track_ids[0].duration, 70.0,
                          'No duration task')
