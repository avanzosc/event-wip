# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api
from openerp.addons.event_track_assistant._common import _convert_to_local_date


class WizEventRegistrationConfirm(models.TransientModel):
    _inherit = 'wiz.event.registration.confirm'

    @api.multi
    def action_confirm_registrations(self):
        self.ensure_one()
        registration_obj = self.env['event.registration']
        presence_obj = self.env['event.track.presence']
        for reg in registration_obj.browse(
            self.env.context.get('active_ids')).filtered(
                lambda x: x.state == 'draft' and x.replaces_to):
            tz = self.env.user.tz
            from_date = _convert_to_local_date(reg.date_start, tz)
            to_date = _convert_to_local_date(reg.date_end, tz)
            cond = [('event', '=', reg.event_id.id),
                    ('partner', '=', reg.replaces_to.id),
                    ('session_date_without_hour', '>=', from_date),
                    ('session_date_without_hour', '<=', to_date)]
            presences = presence_obj.search(cond)
            presences.write({'replaced_by': reg.partner_id.id})
            if presences:
                reg.event_id._send_email_to_employees_substitution(
                    reg.replaces_to, reg.partner_id, presences)
        return super(
            WizEventRegistrationConfirm, self).action_confirm_registrations()

    def _prepare_data_confirm_assistant(self, reg):
        res = super(WizEventRegistrationConfirm,
                    self)._prepare_data_confirm_assistant(reg)
        res['replaces_to'] = reg.replaces_to.id or False
        return res
