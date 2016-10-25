# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from openerp import fields, exceptions


class TestEventLocationManager(common.TransactionCase):

    def setUp(self):
        super(TestEventLocationManager, self).setUp()
        location_model = self.env['event.track.location']
        self.now = fields.Datetime.from_string(fields.Datetime.now())
        self.event = self.env['event.event'].create({
            'name': 'Test Event',
            'date_begin': self.now.replace(day=1),
            'date_end': self.now.replace(day=25),
        })
        self.location1 = location_model.create({
            'name': 'Location 1',
            'capacity': 10,
        })
        self.location2 = location_model.create({
            'name': 'Location 2',
            'capacity': 25,
            'reservation_days': [(0, 0, {'day': self.now.replace(day=10),
                                         'duration': 2.0})]
        })
        self.track_model = self.env['event.track']

    def test_create_track_with_available_location(self):
        track = self.track_model.create({
            'name': 'Test Track',
            'event_id': self.event.id,
            'location_id': self.location1.id,
            'date': self.now.replace(day=10),
            'duration': 1.0,
        })
        self.assertEquals(track.location_id, self.location1)
        self.assertNotEquals(len(track.location_id.reservation_days), 0)

    def test_create_track_with_unavailable_location(self):
        with self.assertRaises(exceptions.Warning):
            self.track_model.create({
                'name': 'Test Track',
                'event_id': self.event.id,
                'location_id': self.location2.id,
                'date': self.now.replace(day=10),
                'duration': 1.0,
            })
