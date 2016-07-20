# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizPutPresenceAsWorked(models.TransientModel):
    _name = 'wiz.put.presence.as.worked'

    name = fields.Char(string='Description')

    @api.multi
    def button_put_presences_as_worked(self):
        day_obj = self.env['res.partner.calendar.day']
        self.ensure_one()
        for day in day_obj.browse(self.env.context.get('active_ids')):
            presences = day.presences.filtered(lambda x: x.state == 'pending')
            presences.write({'state': 'completed'})
            presences = day.presences.filtered(lambda x: not x.absence_type)
            for presence in presences:
                presence._update_presence_duration(presence.session_duration)
