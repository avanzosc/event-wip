# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizChangeSessionDuration(models.TransientModel):
    _name = 'wiz.change.session.duration'

    new_duration = fields.Float(string='New duration')

    @api.multi
    def change_session_duration(self):
        self.ensure_one()
        sessions = self.env['event.track'].browse(
            self.env.context.get('active_ids'))
        sessions.write({'duration': self.new_duration})
