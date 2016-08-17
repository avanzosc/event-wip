# -*- coding: utf-8 -*-
# (c) 2025 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields
from dateutil.relativedelta import relativedelta
import time


class TestEventRegistrationPaCode(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationPaCode, self).setUp()
        self.task_model = self.env['project.task']
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.project_model = self.env['project.project']
        self.event_model = self.env['event.event']
        self.task_model = self.env['project.task']
        self.procurement_model = self.env['procurement.order']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.registration_model = self.env['event.registration']
        self.fec_ini = time.strftime('%Y-%m-%d')
        self.fec_end = (fields.Date.from_string(str(self.fec_ini)) +
                        (relativedelta(months=2)))
        service_product = self.env.ref('product.product_product_consultant')
        service_product.write({'performance': 5.0,
                               'recurring_service': True})
        service_product.performance = 5.0
        service_product.route_ids = [
            (6, 0,
             [self.ref('procurement_service_project.route_serv_project')])]
        self.partner = self.env.ref('base.res_partner_1')
        self.partner.birthdate_date = (fields.Date.to_string(
            fields.Date.from_string(str(self.fec_ini)) +
            relativedelta(years=-3)))
        sale_vals = {
            'name': 'sale order 2',
            'partner_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'project_by_task': 'yes',
            'payer': 'student'}
        sale_line_vals = {
            'partner_id': self.partner.id,
            'product_id': service_product.id,
            'name': service_product.name,
            'product_uom_qty': 7,
            'product_uos_qty': 7,
            'product_uom': service_product.uom_id.id,
            'price_unit': service_product.list_price,
            'performance': 5.0,
            'january': True,
            'february': True,
            'week4': True,
            'week5': True,
            'tuesday': True,
            'thursday': True,
            'start_date': self.fec_ini,
            'start_hour': 8.00,
            'end_date': self.fec_end,
            'end_hour': 12.00}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)

    def test_event_registration_pa_code(self):
        self.sale_order.action_button_confirm()
        event = self.sale_order.order_line[0].event_id
        self.assertNotEqual(event, False, 'Event no generated')
        wiz_vals = {'min_event': event.id,
                    'max_event': event.id,
                    'min_from_date': "{} {}".format(self.fec_ini, '00:00:00'),
                    'max_to_date': "{} {}".format(self.fec_end, '00:00:00'),
                    'from_date': "{} {}".format(self.fec_ini, '00:00:00'),
                    'to_date': "{} {}".format(self.fec_end, '00:00:00'),
                    'partner': self.partner.id}
        wiz = self.wiz_add_model.with_context(
            {'active_ids': [event.id]}).create(wiz_vals)
        wiz.with_context({'active_ids': [event.id]}).action_append()
        event.button_duplicate_ticket()
