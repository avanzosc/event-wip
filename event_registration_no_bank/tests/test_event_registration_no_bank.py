# -*- coding: utf-8 -*-
# Copyright Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventRegistrationNoBank(common.TransactionCase):

    def setUp(self):
        super(TestEventRegistrationNoBank, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.event = self.env.ref('event.event_1')
        self.partner = self.env.ref('base.res_partner_address_23')

    def test_event_registration_no_bank(self):
        cond = [('payer', '=', 'student')]
        self.event.sale_order = self.sale_order_model.search(cond, limit=1)
        self.event.registration_ids[0].partner_id = self.partner.id
        self.event.registration_ids[0].with_context(
            check_mandate_sepa=True).registration_open()
        self.event.registration_ids[0].registration_open()
