# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.depends('task_id', 'task_id.code')
    def _compute_lit_task_code(self):
        for track in self:
            track.lit_task_code = u", {} {} ".format(_('Task code:'),
                                                     track.task_id.code)

    lit_task_code = fields.Char(
        string='Task code literal', compute='_compute_lit_task_code',
        store=True)
