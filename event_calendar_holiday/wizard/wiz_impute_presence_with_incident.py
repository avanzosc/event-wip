# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizImputePresenceWithIncident(models.TransientModel):
    _name = 'wiz.impute.presence.with.incident'

    lines = fields.One2many(
        comodel_name='wiz.impute.presence.with.incident.line',
        inverse_name='wiz_id', string='Presences')

    @api.model
    def default_get(self, var_fields):
        day_obj = self.env['res.partner.calendar.day']
        vals = []
        for day in day_obj.browse(self.env.context.get('active_ids')):
            presences = day.presences.filtered(lambda x: x.state != 'canceled')
            for presence in presences:
                line_vals = {'presence': presence.id,
                             'session': presence.session.id,
                             'session_date': presence.session_date,
                             'notes': presence.notes}
                if presence.real_duration > 0:
                    line_vals['hours'] = presence.real_duration
                else:
                    line_vals['hours'] = presence.session_duration
                vals.append(line_vals)
        return {'lines': vals}

    @api.multi
    def button_impute_hours(self):
        self.ensure_one()
        for wiz in self:
            for line in wiz.lines:
                line.presence.write({'state': 'completed',
                                     'real_duration': line.hours,
                                     'notes': line.notes})


class WizImputePresenceWithIncidentLine(models.TransientModel):
    _name = 'wiz.impute.presence.with.incident.line'

    wiz_id = fields.Many2one(
        comodel_name='wiz.impute.presence.with.incident',
        string='Wizard')
    presence = fields.Many2one(
        'event.track.presence', string='Presence')
    session = fields.Many2one(
        'event.track', string='Session')
    session_date = fields.Datetime('Session date')
    hours = fields.Float('Hours')
    notes = fields.Char('Notes')
