# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta


class EventEvent(models.Model):
    _inherit = 'event.event'

    warnings_not_imputations_count = fields.Integer(
        string='Warnings not imputations count', default=0)


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.multi
    def _search_no_imputations_and_create_claim(self):
        track_obj = self.env['event.track']
        session_date = fields.Date.to_string(fields.Date.from_string(
            fields.Date.context_today(self)) + relativedelta(days=-2))
        cond = [('session_date', '=', session_date)]
        for track in track_obj.search(cond):
            try:
                tracks = track_obj
                if track._find_pending_presences():
                    track.event_id.warnings_not_imputations_count += 1
                if track.event_id.warnings_not_imputations_count < 3:
                    continue
                tracks += track
                previous_track = self._find_previous_track(
                    track.event_id, track.session_date)
                if previous_track and previous_track._find_pending_presences():
                    tracks += previous_track
                if previous_track:
                    previous_track = self._find_previous_track(
                        previous_track.event_id, previous_track.session_date)
                    if (previous_track and
                            previous_track._find_pending_presences()):
                        tracks += previous_track
                for track in tracks:
                    track._create_claim_not_imputation()
                track.event_id.warnings_not_imputations_count = 0
            except Exception:
                continue

    def _find_pending_presences(self):
        if any(self.mapped('presences').filtered(
                lambda l: l.state == 'pending')):
            return True
        return False

    def _find_previous_track(self, event, date):
        previous_track = False
        previous_tracks = event.track_ids.filtered(
            lambda x: x.session_date and x.session_date < date)
        if previous_tracks:
            previous_track = max(previous_tracks, key=lambda x: x.session_date)
        return previous_track

    def _create_claim_not_imputation(self):
        mail_obj = self.env['mail.mail']
        try:
            categ_id = self.env.ref(
                'event_track_presence_claim.crm_case_categ_pending_registrati'
                'ons_presences').id
        except Exception:
            categ_id = False
        teacher_presences = self.presences.filtered(
            lambda x: x.state not in ('absent', 'canceled') and x.employee)
        if not teacher_presences:
            return True
        teacher_presence = min(teacher_presences, key=lambda x: x.id)
        name = (_(u'Pending recording assists at the event: %s') %
                (self.event_id.name))
        description = _(
            u'This claim is generated because you are not following the '
            'attendance registration procedure. We remind you that it is '
            'essential to keep up to date the assistances of the students of'
            ' your classes. You have pending without registering the following'
            ' sessions:\n')
        session = _(u'- {}, date: {}.').format(self.name, self.session_date)
        description = u"{}\n{}".format(description, session)
        description = u"{}\n\n{}".format(
            description,
            _(u'You have 48 hours to register attendance. Please get up to '
              'speed as soon as possible, or contact the group coordinator if '
              'you have a problem that prevents you from doing so.'))
        description = u"{}\n\n{}".format(
            description, _('Regards.'))
        vals = ({
            'name': name,
            'description': description,
            'event_id': self.event_id.id,
            'session_id': self.id,
            'user_id': self.event_id.user_id.id})
        if categ_id:
            vals['categ_id'] = categ_id
        claim = self.env['crm.claim'].with_context(
            tracking_disable=True).create(vals)
        claim.message_follower_ids = [
            (6, 0, [teacher_presence.partner.id,
                    self.event_id.user_id.partner_id.id])]
        subject = _(u'This claim has been created: {}.').format(claim.name)
        values = {'subject': subject,
                  'body': claim.description,
                  'body_html': claim.description,
                  'notification': True,
                  'model': 'crm.claim',
                  'res_id': claim.id,
                  'recipient_ids': [(6, 0, claim.message_follower_ids.ids)]}
        mail = mail_obj.create(values)
        mail.send()
