# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


class WizChangeSessionDate(models.TransientModel):
    _name = 'wiz.change.session.date'

    days = fields.Integer(
        string='Days', required=True, help=_('Positive sum days, negative'
                                             ' subtraction days'))

    @api.multi
    def change_session_date(self):
        self.ensure_one()
        session_obj = self.env['event.track']
        sessions = session_obj.browse(
            self.env.context.get('active_ids')).filtered(
            lambda x: x.stage_id !=
            self.env.ref('website_event_track.event_track_stage5').id)
        for session in sessions:
            count = len(session.presences.filtered(
                lambda x: x.state == 'completed'))
            if count > 0:
                raise exceptions.Warning(
                    _('You can not change the date of the session: %s, of'
                      ' event %s, because session has made assists')
                    % (session.name, session.event_id.name))
            session._change_session_date(self.days)
