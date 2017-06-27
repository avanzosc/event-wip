# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.tests.common import TransactionCase


class TestEventTrackPresenceCustomerInfo(TransactionCase):

    def setUp(self):
        super(TestEventTrackPresenceCustomerInfo, self).setUp()
        self.sale_model = self.env['sale.order']
        self.event_model = self.env['event.event']
        self.presence_model = self.env['event.track.presence']
        self.customer = self.browse_ref('base.res_partner_18')
        sale_vals = {'partner_id': self.customer.id}
        self.sale = self.sale_model.create(sale_vals)
        event_vals = {'name': 'Test event track presence customer info',
                      'date_begin': '2025-01-10 15:00:00',
                      'date_end': '2025-01-20 16:00:00',
                      'sale_order': self.sale.id}
        session_vals = {'name': 'event session',
                        'date': '2025-01-10 15:00:00',
                        'session_date': '2025-01-10',
                        'duration': 1}
        event_vals['track_ids'] = [(0, 0, session_vals)]
        self.event = self.event_model.create(event_vals)

    def test_event_track_presence_customer_info(self):
        presence_vals = {'event': self.event.id,
                         'session': self.event.track_ids[0].id,
                         'session_duration': 1,
                         'partner': self.customer.id}
        presence = self.presence_model.create(presence_vals)
        if self.customer.street:
            self.assertIn(
                self.customer.street, presence.customer_street,
                'Bad street in customer presence')
        if self.customer.zip:
            self.assertIn(
                self.customer.zip, presence.customer_street,
                'Bad zip in customer presence')
        if self.customer.city:
            self.assertIn(
                self.customer.city, presence.customer_street,
                'Bad city in customer presence')
