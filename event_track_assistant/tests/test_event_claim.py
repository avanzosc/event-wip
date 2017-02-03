# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestEventClaim(common.TransactionCase):

    def setUp(self):
        super(TestEventClaim, self).setUp()
        user_model = self.env['res.users']
        event_model = self.env['event.event']
        self.claim_model = self.env['crm.claim']
        self.user1 = user_model.create({
            'name': 'User One',
            'login': 'user1',
        })
        self.user2 = user_model.create({
            'name': 'User Two',
            'login': 'user2',
        })
        event_vals = {
            'name': 'Registration partner test',
            'user_id': self.user1.id,
            'date_begin': '2025-01-20',
            'date_end': '2025-01-30',
            'track_ids': [(0, 0, {'name': 'Session 1',
                                  'date': '2025-01-22 00:00:00',
                                  'user_id': self.user2.id}),
                          (0, 0, {'name': 'Session 2',
                                  'date': '2025-01-25 00:00:00',
                                  'user_id': self.user1.id}),
                          (0, 0, {'name': 'Session 3',
                                  'date': '2025-01-28 00:00:00',
                                  'user_id': self.user1.id})]
        }
        self.event = event_model.create(event_vals)

    def test_claim_onchange_event_id(self):
        claim = self.claim_model.create({
            'name': 'New Claim',
        })
        self.assertEquals(claim.user_id, self.env.user)
        self.assertFalse(claim.event_id)
        self.assertFalse(claim.session_id)
        claim.write({
            'event_id': self.event.id,
        })
        claim._onchange_event_id()
        self.assertEquals(claim.user_id, self.user1)
        self.assertTrue(claim.event_id)
        self.assertFalse(claim.session_id)

    def test_claim_onchange_session_id(self):
        claim = self.claim_model.create({
            'name': 'New Claim',
        })
        self.assertEquals(claim.user_id, self.env.user)
        self.assertFalse(claim.event_id)
        self.assertFalse(claim.session_id)
        claim.write({
            'session_id': self.event.track_ids[:1].id,
        })
        claim._onchange_session_id()
        self.assertEquals(claim.user_id, self.user2)
        self.assertTrue(claim.event_id)
        self.assertTrue(claim.session_id)

    def test_claim_onchanges_event_session(self):
        claim = self.claim_model.create({
            'name': 'New Claim',
        })
        self.assertEquals(claim.user_id, self.env.user)
        self.assertFalse(claim.event_id)
        self.assertFalse(claim.session_id)
        claim.write({
            'event_id': self.event.id,
        })
        claim._onchange_event_id()
        self.assertEquals(claim.user_id, self.user1)
        self.assertTrue(claim.event_id)
        self.assertFalse(claim.session_id)
        claim.write({
            'session_id': self.event.track_ids[:1].id,
        })
        claim._onchange_session_id()
        self.assertEquals(claim.user_id, self.user2)
        self.assertTrue(claim.event_id)
        self.assertTrue(claim.session_id)

    def test_claim_onchanges_session_event(self):
        claim = self.claim_model.create({
            'name': 'New Claim',
        })
        self.assertEquals(claim.user_id, self.env.user)
        self.assertFalse(claim.event_id)
        self.assertFalse(claim.session_id)
        claim.write({
            'session_id': self.event.track_ids[:1].id,
        })
        claim._onchange_session_id()
        self.assertEquals(claim.user_id, self.user2)
        self.assertTrue(claim.event_id)
        self.assertTrue(claim.session_id)
        claim.write({
            'event_id': self.event.id,
        })
        claim._onchange_event_id()
        self.assertEquals(claim.user_id, self.user2)
        self.assertTrue(claim.event_id)
        self.assertTrue(claim.session_id)
