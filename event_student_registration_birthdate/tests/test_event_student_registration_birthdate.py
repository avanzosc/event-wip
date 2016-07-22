# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventStudendRegistrationBirthdate(common.TransactionCase):

    def setUp(self):
        super(TestEventStudendRegistrationBirthdate, self).setUp()
        self.registration_model = self.env['event.registration']
        self.partner = self.env.ref('base.res_partner_26')
        partner_vals = {'parent_id': 1,
                        'is_group': False,
                        'is_company': False,
                        'birthdate_date': '2005-01-15'}
        self.partner.write(partner_vals)

    def test_event_student_registration_birthdate(self):
        registration_vals = {'event_id': self.ref('event.event_3'),
                             'partner_id': self.partner.id}
        registration = self.registration_model.create(registration_vals)
        self.assertNotEqual(
            registration, False, 'Partner no registered in event')
