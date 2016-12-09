# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields, exceptions


class TestEventRegistrationSepa(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationSepa, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.event = self.env.ref('event.event_1')
        self.partner = self.env.ref('base.res_partner_address_23')
        self.partner.parent_id.bank_ids = self.env['res.partner.bank'].create({
            'acc_number': 'ES9121000418450200051332',
            'partner_id': self.partner.id,
            'state': 'iban',
            'mandate_ids': [(0, 0, {
                'format': 'sepa',
                'signature_date': fields.Date.today(),
            })],
        })

    def test_mandate_sepa_payer_student_registration_student(self):
        cond = [('payer', '=', 'student')]
        self.event.sale_order = self.sale_order_model.search(cond, limit=1)
        registration = self.event.registration_ids[0].with_context(
            check_mandate_sepa=True)
        registration.partner_id = self.partner
        self.assertEqual(registration.parent_num_valid_mandates, 0)
        with self.assertRaises(exceptions.Warning):
            registration.registration_open()
        self.partner.parent_id.bank_ids[0].mandate_ids[0].validate()
        self.assertEqual(registration.parent_num_valid_mandates, 1)
        self.assertEqual(registration.state, 'draft')
        registration.registration_open()
        self.assertEqual(registration.state, 'open')

    def test_mandate_sepa_payer_student_registration_teacher(self):
        cond = [('payer', '=', 'student')]
        self.event.sale_order = self.sale_order_model.search(cond, limit=1)
        registration = self.event.registration_ids[0].with_context(
            check_mandate_sepa=True)
        registration.partner_id = self.partner
        registration.partner_id.employee_id = self.env.ref('hr.employee_al')
        registration.registration_open()
        self.assertEqual(registration.state, 'open')

    def test_mandate_sepa_payer_school_registration_student(self):
        cond = [('payer', '=', 'school')]
        self.event.sale_order = self.sale_order_model.search(cond, limit=1)
        registration = self.event.registration_ids[0].with_context(
            check_mandate_sepa=True)
        registration.partner_id = self.partner
        self.assertEqual(registration.parent_num_valid_mandates, 0)
        registration.registration_open()
        self.assertEqual(registration.state, 'open')

    def test_mandate_sepa_payer_school_registration_teacher(self):
        cond = [('payer', '=', 'school')]
        self.event.sale_order = self.sale_order_model.search(cond, limit=1)
        registration = self.event.registration_ids[0].with_context(
            check_mandate_sepa=True)
        registration.partner_id = self.partner
        registration.partner_id.employee_id = self.env.ref('hr.employee_al')
        registration.registration_open()
        self.assertEqual(registration.state, 'open')
