# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    event_id = fields.Many2one(comodel_name='event.event', string='Event')
    session_id = fields.Many2one(comodel_name='event.track', string='Session')
    event_state = fields.Selection(
        string='Event state', related='event_id.state', store=True)

    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_id:
            self.user_id = self.session_id.user_id or self.event_id.user_id or\
                self.env.user
            self.session_id = False if self.session_id and\
                self.session_id.event_id != self.event_id else self.session_id
            return {'domain':
                    {'session_id': [('event_id', '=', self.event_id.id)]}}
        return {'domain':
                {'session_id': []}}

    @api.onchange('session_id')
    def _onchange_session_id(self):
        if self.session_id:
            self.event_id = self.session_id.event_id if not self.event_id else\
                self.event_id
            self.user_id = self.session_id.user_id or\
                self.session_id.event_id.user_id or self.env.user
