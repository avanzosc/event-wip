# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class WizEventTrackMerge(models.TransientModel):
    _name = 'wiz.event.track.merge'
    _description = 'Wizard for merge event tracks'

    name = fields.Char(string="Description")

    @api.multi
    def buttom_merge_event_tracks(self):
        self.ensure_one()
        events = self.env['event.event'].browse(
            self.env.context.get('active_ids'))
        events._merge_event_tracks()
