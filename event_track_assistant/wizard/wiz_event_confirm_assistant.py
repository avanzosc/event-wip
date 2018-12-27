# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizEventConfirmAssistant(models.TransientModel):
    _name = 'wiz.event.confirm.assistant'

    name = fields.Char(string='Description')

    @api.multi
    def action_confirm_assistant(self):
        self.ensure_one()
        event_obj = self.env['event.event']
        track_obj = self.env['event.track']
        append_obj = self.env['wiz.event.append.assistant']
        for event in event_obj.browse(self.env.context.get('active_ids')):
            registrations = self._select_event_registrations(event)
            for reg in registrations:
                append_vals = self._prepare_data_confirm_assistant(reg)
                append = append_obj.create(append_vals)
                registration = append._update_create_registration(reg.event_id,
                                                                  reg)
                registration.confirm_registration()
                registration.mail_user()
                cond = append._prepare_track_condition_search(reg.event_id)
                tracks = track_obj.search(cond)
                for track in tracks:
                    presence = track.presences.filtered(
                        lambda x: x.session == track and
                        x.event == reg.event_id and
                        x.partner == append.partner)
                    if presence:
                        append._put_pending_presence_state(presence)
                    else:
                        append._create_presence_from_wizard(track,
                                                            reg.event_id)

    def _select_event_registrations(self, event):
        registrations = event.registration_ids.filtered(
            lambda x: x.state == 'draft')
        return registrations

    def _prepare_data_confirm_assistant(self, reg):
        append_vals = {'from_date': reg.date_start,
                       'min_from_date': reg.date_start,
                       'to_date': reg.date_end,
                       'max_to_date': reg.date_end,
                       'registration': reg.id,
                       'partner': reg.partner_id.id,
                       'min_event': reg.event_id.id,
                       'max_event': reg.event_id.id}
        return append_vals
