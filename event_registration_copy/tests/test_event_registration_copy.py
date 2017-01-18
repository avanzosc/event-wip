# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventRegistrationCopy(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationCopy, self).setUp()
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.event_model = self.env['event.event']
        self.registration_model = self.env['event.registration']
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2025-01-15',
                        'date': '2025-02-28',
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
            'name': 'sale order test event_registration_copy',
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
            'january': True,
            'february': True,
            'week4': True,
            'week5': True,
            'tuesday': True,
            'thursday': True,
            'start_date': '2025-01-15',
            'start_hour': 8.00,
            'end_date': '2025-02-28',
            'end_hour': 09.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_event_registration_copy(self):
        self.sale_order.action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        event = self.event_model.search(cond, limit=1)[:1]
        self.assertNotEqual(
            len([event]), 0, 'Sale order without event')
        registration_vals = ({'event_id': event.id,
                              'partner_id':
                              self.env.ref('base.res_partner_25').id,
                              'state': 'draft',
                              'date_start': '2025-01-15 08:00:00',
                              'date_end': '2025-02-28 09:00:00'})
        registration = self.registration_model.create(registration_vals)
        wiz_vals = {'name': 'confirm assistants'}
        wiz = self.wiz_confirm_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': [event.id]}).action_confirm_assistant()
        self.assertNotEqual(
            registration.state, 'draft', 'Registration not confirmed')
        copy_sale_order = self.sale_order.copy()
        self.assertEquals(copy_sale_order.state, 'draft')
        account_vals = {'name': 'account procurement service project',
                        'date_start': '2025-01-15',
                        'date': '2025-02-28',
                        'use_tasks': True}
        copy_sale_order.project_id = self.account_model.create(account_vals)
        copy_sale_order.action_button_confirm()
        cond = [('sale_order', '=', copy_sale_order.id)]
        new_event = self.event_model.search(cond, limit=1)[:1]
        self.assertEqual(
            len(event.registration_ids),
            len(new_event.registration_ids),
            'Old event and new event with distinct registrations')
