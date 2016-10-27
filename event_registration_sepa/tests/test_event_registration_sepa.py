# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields, exceptions


class TestEventRegistrationSepa(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationSepa, self).setUp()
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

    def test_mandate_sepa(self):
        registration = self.event.registration_ids[0].with_context(
            check_mandate_sepa=True)
        registration.partner_id = self.partner
        self.assertEqual(registration.sepa_draft, 1)
        self.assertEqual(registration.sepa_active, 0)
        with self.assertRaises(exceptions.Warning):
            registration.registration_open()
        self.partner.parent_id.bank_ids[0].mandate_ids[0].validate()
        self.assertEqual(registration.sepa_draft, 0)
        self.assertEqual(registration.sepa_active, 1)
        self.assertEqual(registration.state, 'draft')
        registration.registration_open()
        self.assertEqual(registration.state, 'open')
