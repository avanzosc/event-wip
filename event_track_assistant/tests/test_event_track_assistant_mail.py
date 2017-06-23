# -*- coding: utf-8 -*-
# Copyright 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import exceptions
from .common import EventTrackAssistantSetup


class TestEventTrackAssistantMail(EventTrackAssistantSetup):

    def setUp(self):
        super(TestEventTrackAssistantMail, self).setUp()

    def test_send_email_to_event_organizer(self):
        self.event.organizer_id.write({'email': False,
                                       'notify_email': 'none'})
        with self.assertRaises(exceptions.Warning):
            self.event.button_mass_mailing_to_organizer()
        self.event.organizer_id.notify_email = 'always'
        with self.assertRaises(exceptions.Warning):
            self.event.button_mass_mailing_to_organizer()
        self.event.organizer_id.email = 'test@test.com'
        res = self.event.button_mass_mailing_to_organizer()
        context = res.get('context')
        self.assertEqual(
            context.get('default_composition_mode'), 'mass_mail',
            'Bad composition mode to send email')
        self.assertEqual(
            context.get('default_model'), 'event.event',
            'Bad model to send email')
        self.assertEqual(
            context.get('default_res_id'), self.event.id,
            'Bad event to send email')

    def test_send_email_to_event_registrations(self):
        registration_vals = {
            'event_id': self.event.id,
            'partner_id': self.partner.id,
        }
        self.registration_model.create(registration_vals)
        self.partner.write({'email': False,
                            'notify_email': 'always'})
        with self.assertRaises(exceptions.Warning):
            self.event.button_mass_mailing_to_registrations()
        self.partner.email = 'test@test.com'
        wiz = self.wiz_email_model.create({})
        wiz.default_get(['body'])
        wiz.with_context(active_id=self.event.id).button_send_email()
        res = self.event.button_mass_mailing_to_registrations()
        context = res.get('context')
        self.assertEqual(
            context.get('active_model'), 'event.event',
            'Bad model to send email')
        self.assertEqual(
            context.get('active_id'), self.event.id,
            'Bad event to send email')
        self.assertEqual(
            res.get('res_model'), 'wiz.send.email.to.registrations',
            'Bad res_model to send email')
