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
        self.event.registration_ids[0].partner_id = self.partner
        self.assertEqual(self.event.registration_ids[0].sepa_draft, 1)
        self.assertEqual(self.event.registration_ids[0].sepa_active, 0)
        with self.assertRaises(exceptions.Warning):
            self.event.registration_ids[0].registration_open()
        self.partner.parent_id.bank_ids[0].mandate_ids[0].validate()
        self.assertEqual(self.event.registration_ids[0].sepa_draft, 0)
        self.assertEqual(self.event.registration_ids[0].sepa_active, 1)
        self.assertEqual(self.event.registration_ids[0].state, 'draft')
        self.event.registration_ids[0].registration_open()
        self.assertEqual(self.event.registration_ids[0].state, 'open')
