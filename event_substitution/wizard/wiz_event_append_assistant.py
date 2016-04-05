# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    replaces_to = fields.Many2one('res.partner', strint='Replaces to')

    @api.multi
    def action_append(self):
        self.ensure_one()
        res = super(WizEventAppendAssistant, self).action_append()
        presence_obj = self.env['event.track.presence']
        if self.registration and self.replaces_to:
            from_date, to_date = self._calc_dates_for_search_track(
                self.from_date, self.to_date)
            cond = [('event', '=', self.registration.event_id.id),
                    ('partner', '=', self.replaces_to.id),
                    ('session_date_without_hour', '>=', from_date),
                    ('session_date_without_hour', '<=', to_date)]
            presences = presence_obj.search(cond)
            presences.write({'replaced_by': self.partner.id})
        return res

    def _create_presence_from_wizard(self, track, event):
        presence = super(WizEventAppendAssistant,
                         self)._create_presence_from_wizard(track, event)
        if self.replaces_to:
            presence.replaces_to = self.replaces_to.id
        return presence

    def _put_pending_presence_state(self, presence):
        res = super(WizEventAppendAssistant,
                    self)._put_pending_presence_state(presence)
        if self.replaces_to:
            presence.replaces_to = self.replaces_to.id
        return res
