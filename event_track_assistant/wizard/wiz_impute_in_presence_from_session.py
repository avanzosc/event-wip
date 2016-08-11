# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizImputeInPresenceFromSession(models.TransientModel):
    _name = 'wiz.impute.in.presence.from.session'

    lines = fields.One2many(
        comodel_name='wiz.impute.in.presence.from.session.line',
        inverse_name='wiz_id', string='Presences')

    @api.model
    def default_get(self, var_fields):
        res = super(WizImputeInPresenceFromSession,
                    self).default_get(var_fields)
        track_obj = self.env['event.track']
        vals = []
        for track in track_obj.browse(self.env.context.get('active_ids')):
            presences = track.presences.filtered(
                lambda x: x.state != 'canceled')
            for presence in presences:
                line_vals = {
                    'presence': presence.id,
                    'session': presence.session.id,
                    'session_date': presence.session_date,
                    'partner': presence.partner.id,
                    'notes': presence.notes,
                    'hours': presence.real_duration
                    if presence.real_duration > 0 else
                    presence.session_duration}
                vals.append(line_vals)
        res.update(lines=vals)
        return res

    @api.multi
    def button_impute_hours(self):
        work_obj = self.env['project.task.work']
        for line in self.mapped('lines'):
            hours = line.hours if not line.unassisted else 0.0
            line.presence._update_presence_duration(
                hours, state='completed' if not line.unassisted else 'pending',
                notes=line.notes)
            if line.partner.employee_id and line.hours:
                work_vals = {'event_id': line.session.event_id.id,
                             'date': line.session.real_date_end,
                             'task_id': line.session.tasks[:1].id,
                             'name': line.session.name,
                             'hours': line.hours,
                             'user_id': line.partner.employee_id.user_id.id}
                work_obj.create(work_vals)
                line.session.stage_id = self.env.ref(
                    'website_event_track.event_track_stage5').id


class WizImputeInPresenceFromSessionLine(models.TransientModel):
    _name = 'wiz.impute.in.presence.from.session.line'

    wiz_id = fields.Many2one(
        comodel_name='wiz.impute.in.presence.from.session', string='Wizard',
        ondelete='cascade')
    presence = fields.Many2one('event.track.presence', string='Presence')
    session = fields.Many2one('event.track', string='Session')
    session_date = fields.Datetime('Session date')
    partner = fields.Many2one('res.partner', string='Partner')
    unassisted = fields.Boolean(string='Unassisted', default=False)
    hours = fields.Float('Hours')
    notes = fields.Char('Notes')
