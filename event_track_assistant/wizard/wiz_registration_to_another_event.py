# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizRegistrationToAnotherEvent(models.TransientModel):
    _name = 'wiz.registration.to.another.event'

    new_event_id = fields.Many2one(
        string='New event for the registration', comodel_name='event.event',
        required=True)

    @api.model
    def default_get(self, var_fields):
        res = super(
            WizRegistrationToAnotherEvent, self).default_get(var_fields)
        registration = self.env['event.registration'].browse(
            self.env.context['active_id'])
        res.update({
            'event_registration_id': registration.id,
            'event_id': registration.event_id.id,
        })
        return res

    @api.multi
    def button_change_registration_event(self):
        confirm_obj = self.env['wiz.event.confirm.assistant']
        append_obj = self.env['wiz.event.append.assistant']
        track_obj = self.env['event.track']
        registrations = self.env['event.registration'].browse(
            self.env.context['active_ids']).filtered(
            lambda x: x.state in ('draft', 'open'))
        for registration in registrations:
            registration.event_id.mapped('track_ids.presences').filtered(
                lambda x: x.partner == registration.partner_id and
                x.state == 'pending').button_canceled()
            self._change_registration_event(registration)
            if registration.state == 'open':
                registration.state = 'draft'
                append_vals = confirm_obj._prepare_data_confirm_assistant(
                    registration)
                append = append_obj.create(append_vals)
                reg = append._update_create_registration(
                    registration.event_id, registration)
                reg.confirm_registration()
                reg.mail_user()
                cond = append._prepare_track_condition_search(
                    self.new_event_id)
                tracks = track_obj.search(cond)
                for track in tracks:
                    presence = track.presences.filtered(
                        lambda x: x.session == track and
                        x.event == self.new_event_id and
                        x.partner == registration.partner_id)
                    if presence:
                        append._put_pending_presence_state(presence)
                    else:
                        append._create_presence_from_wizard(
                            track, self.new_event_id)

    def _change_registration_event(self, registration):
        registration.write({
            'event_id': self.new_event_id.id,
            'date_start': self.new_event_id.date_begin,
            'date_end': self.new_event_id.date_end,
        })
