# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common


class EventTrackAssistantSetup(common.TransactionCase):

    def setUp(self):
        super(EventTrackAssistantSetup, self).setUp()
        self.env.user.write({
            'tz': u'UTC',
        })
        self.event_model = self.env['event.event']
        self.presence_model = self.env['event.track.presence']
        self.registration_model = self.env['event.registration']
        self.wiz_add_model = self.env['wiz.event.append.assistant']
        self.wiz_del_model = self.env['wiz.event.delete.assistant']
        self.wiz_confirm_model = self.env['wiz.event.confirm.assistant']
        self.wiz_impute_model = self.env['wiz.impute.in.presence.from.session']
        self.wiz_change_event_model =\
            self.env['wiz.registration.to.another.event']
        self.wiz_presence_model = self.env['wiz.complete.presence']
        self.wiz_duration_model = self.env['wiz.change.session.duration']
        self.claim_model = self.env['crm.claim']
        self.partner_model = self.env['res.partner']
        self.config_model = self.env['marketing.config.settings']
        self.wiz_email_model = self.env['wiz.send.email.to.registrations']
        self.parent = self.partner_model.create({
            'name': 'Parent Partner',
        })
        self.partner = self.partner_model.create({
            'name': 'Test Partner',
        })
        event_vals = {
            'name': 'Registration partner test',
            'date_begin': '2025-01-20',
            'date_end': '2025-01-30',
            'track_ids': [(0, 0, {'name': 'Session 1',
                                  'date': '2025-01-22 00:00:00'}),
                          (0, 0, {'name': 'Session 2',
                                  'date': '2025-01-25 00:00:00'}),
                          (0, 0, {'name': 'Session 3',
                                  'date': '2025-01-28 00:00:00'})]
        }
        self.event = self.event_model.create(event_vals)
