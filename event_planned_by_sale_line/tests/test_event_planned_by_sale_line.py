# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.event_registration_analytic.tests.\
    test_event_registration_analytic import TestEventRegistrationAnalytic
from openerp import fields, exceptions
from dateutil.relativedelta import relativedelta


class TestEventPlannedBySaleLine(TestEventRegistrationAnalytic):

    def setUp(self):
        super(TestEventPlannedBySaleLine, self).setUp()
        self.sale_line_model = self.env['sale.order.line']
        self.today = fields.Date.from_string(fields.Date.today())
        partner_model = self.env['res.partner']
        self.parent = partner_model.create({
            'name': 'Parent',
        })
        self.partner = partner_model.create({
            'name': 'Student',
            'is_group': False,
            'is_company': False,
        })
        self.sale_order.write({
            'product_category': self.service_product.categ_id.id,
        })
        self.sale_order.order_line.write({
            'start_date': self.today - relativedelta(years=1),
            'end_date': self.today + relativedelta(months=2),
        })
        self.quote_template = self.env['sale.quote.template'].create({
            'name': 'Quote Template',
            'quote_line': [(0, 0, {
                'name': self.service_product.name,
                'product_id': self.service_product.id,
                'product_uom_id': self.service_product.uom_id.id,
                'price_unit': self.service_product.lst_price,
            })],
        })

    def test_event_planned_by_sale_line(self):
        account = self.sale_order.project_id
        self.sale_order.write({
            'project_by_task': 'yes',
            'payer': 'school',
            'project_id': False,
        })
        self.assertFalse(self.sale_order.project_id)
        self.sale_order.with_context(
            check_automatic_contract_creation=True).action_button_confirm()
        self.assertTrue(self.sale_order.project_id)
        self.assertNotEquals(self.sale_order.project_id, account)
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {
            'partner': self.partner.id,
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        wiz.action_append()
        invoice_ids =\
            self.sale_order.project_id.recurring_create_invoice()
        self.assertNotEquals(len(invoice_ids), 0)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            self.assertNotEquals(
                sum(invoice.mapped('invoice_line.quantity')), 0)

    def test_event_planned_by_sale_line_punctual(self):
        self.sale_order.write({
            'project_by_task': 'yes',
            'payer': 'school',
            'project_id': False,
        })
        self.service_product.categ_id.punctual_service = True
        self.sale_order.with_context(
            check_automatic_contract_creation=True).action_button_confirm()
        self.assertEquals(
            self.sale_order.project_id.recurring_rule_type, 'yearly')
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {
            'partner': self.partner.id,
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        wiz.action_append()
        invoice_ids =\
            self.sale_order.project_id.recurring_create_invoice()
        self.assertNotEquals(len(invoice_ids), 0)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            self.assertNotEquals(
                sum(invoice.mapped('invoice_line.quantity')), 0)

    def test_event_planned_by_sale_line_student(self):
        accounts = self.account_model.search(
            [('student', '=', self.partner.id)])
        self.assertEquals(len(accounts), 0)
        self.sale_order.write({
            'project_by_task': 'yes',
            'payer': 'student',
            'project_id': False,
        })
        self.sale_order.with_context(
            check_automatic_contract_creation=True).action_button_confirm()
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {
            'partner': self.partner.id,
            'create_account': True,
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        with self.assertRaises(exceptions.Warning):
            wiz.action_append()
        self.partner.parent_id = self.parent
        wiz.action_append()
        accounts = self.account_model.search(
            [('student', '=', self.partner.id)])
        self.assertNotEquals(len(accounts), 0)
        invoice_ids = accounts[:1].recurring_create_invoice()
        self.assertNotEquals(len(invoice_ids), 0)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            self.assertNotEquals(
                sum(invoice.mapped('invoice_line.quantity')), 0)

    def test_event_planned_by_sale_line_punctual_student(self):
        accounts = self.account_model.search(
            [('student', '=', self.partner.id)])
        self.assertEquals(len(accounts), 0)
        self.sale_order.write({
            'project_by_task': 'yes',
            'payer': 'student',
            'project_id': False,
        })
        self.service_product.categ_id.punctual_service = True
        self.sale_order.with_context(
            check_automatic_contract_creation=True).action_button_confirm()
        self.assertEquals(
            self.sale_order.project_id.recurring_rule_type, 'yearly')
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        wiz_vals = {
            'partner': self.partner.id,
            'create_account': True,
        }
        wiz = self.wiz_add_model.with_context(
            active_ids=events.ids).create(wiz_vals)
        with self.assertRaises(exceptions.Warning):
            wiz.action_append()
        self.partner.parent_id = self.parent
        wiz.action_append()
        accounts = self.account_model.search(
            [('student', '=', self.partner.id)])
        self.assertNotEquals(len(accounts), 0)
        invoice_ids = accounts[:1].recurring_create_invoice()
        self.assertNotEquals(len(invoice_ids), 0)
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            self.assertNotEquals(
                sum(invoice.mapped('invoice_line.quantity')), 0)

    def test_event_planned_by_sale_line_cancel(self):
        self.sale_order.write({
            'project_by_task': 'yes',
            'payer': 'school',
            'project_id': False,
        })
        self.sale_order.with_context(
            check_automatic_contract_creation=True).action_button_confirm()
        self.assertEquals(
            self.sale_order.project_id.recurring_rule_type, 'monthly')
        cond = [('sale_order', '=', self.sale_order.id)]
        events = self.event_model.search(cond)
        self.assertNotEqual(
            len(events), 0, 'Sale order without event')
        self.sale_order.action_cancel()
        self.assertFalse(self.sale_order.project_id)

    def test_onchange_product_category(self):
        categ_all = self.browse_ref('product.product_category_all')
        self.sale_order.product_category = categ_all
        result = self.sale_order.onchange_product_category()
        self.assertIn('warning', result)
        self.assertNotEquals(self.sale_order.product_category, categ_all)

    def test_onchange_start_end_date(self):
        line = self.sale_line_model.new({
            'start_date': self.today.replace(month=3),
            'end_date': self.today.replace(month=7),
        })
        line.onchange_start_end_date()
        self.assertFalse(line.january)
        self.assertFalse(line.february)
        self.assertTrue(line.march)
        self.assertTrue(line.april)
        self.assertTrue(line.may)
        self.assertTrue(line.june)
        self.assertTrue(line.july)
        self.assertFalse(line.august)
        self.assertFalse(line.september)
        self.assertFalse(line.october)
        self.assertFalse(line.november)
        self.assertFalse(line.december)

    def test_onchange_template(self):
        categ_all = self.browse_ref('product.product_category_all')
        order = self.sale_model.new({
            'template_id': self.quote_template.id,
            'product_category': categ_all.id,
            'partner_id': self.sale_order.partner_id.id,
        })
        result = order.onchange_template_id(
            order.template_id.id, partner=order.partner_id.id)
        self.assertTrue('warning' in result)
        result = order.onchange_template_id(
            order.template_id.id, partner=order.partner_id.id,
            product_category=order.product_category.id)
        self.assertFalse('warning' in result)
