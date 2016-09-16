# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


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
        claim_obj = self.env['crm.claim']
        for line in self.mapped('lines'):
            if line.create_claim and not line.notes:
                raise exceptions.Warning(
                    _('To create a claim, you must enter the notes'))
            if line.create_claim:
                claim_obj.create(self._get_values_for_create_claim(line))
            hours = line.hours if not line.unassisted else 0.0
            line.presence._update_presence_duration(
                hours, state='completed' if not line.unassisted else 'pending',
                notes=line.notes)

    def _get_values_for_create_claim(self, line):
        name = _(u'Event: {}, session:{}').format(line.presence.event.name,
                                                  line.presence.session.name)
        description = _(u'SESSION DATE: {}, PERSON: {}, NOTES: {}').format(
            line.presence.session.date, line.presence.partner.name,
            line.notes)
        claim_vals = {'name': name,
                      'user_id': line.presence.event.user_id.id,
                      'partner_id': self.env.user.partner_id.id,
                      'email_from': self.env.user.login,
                      'description': description,
                      'event_id': line.presence.event.id,
                      'session_id': line.presence.session.id,
                      'ref': '{},{}'.format(line.presence._name,
                                            line.presence.id)}
        return claim_vals


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
    create_claim = fields.Boolean(string='Create claim', default=False)
    notes = fields.Char('Notes')
