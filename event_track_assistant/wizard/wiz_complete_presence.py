# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class WizCompletePresence(models.TransientModel):
    _name = 'wiz.complete.presence'
    _description = 'Wizard for complete presences'

    name = fields.Char(string="Description")

    @api.multi
    def buttom_complete_presences(self):
        self.ensure_one()
        presences = self.env['event.track.presence'].browse(
            self.env.context.get('active_ids'))
        presences.button_completed()
