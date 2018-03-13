# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import _, api, fields, models
from openerp.addons.event_track_assistant._common import _convert_to_local_date

date2str = fields.Date.to_string


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def button_validate_holiday(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.substitution']
        line_vals = []
        if (self.state == 'confirm' and self.type == 'remove' and
                self.employee_id.address_home_id):
            events = self._find_events_for_substitution_employee()
            if events:
                wiz = wiz_obj.create({'holiday': self.id})
                for event in events:
                    line_vals.append((0, 0, {'event': event.id}))
                wiz.write({'lines': line_vals})
                context = self.env.context.copy()
                context['active_id'] = self.id
                context['active_ids'] = [self.id]
                context['active_model'] = 'hr.holidays'
                return {'name': _('Wizard for substitution employee in'
                                  ' events'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'wiz.event.substitution',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': wiz.id,
                        'target': 'new',
                        'context': context}
            else:
                self.signal_workflow('validate')
                self._update_presences_validate_holiday()
                self._update_partner_calendar_day(
                    self, absence_type=self.holiday_status_id.id)
        else:
            self.signal_workflow('validate')

    @api.multi
    def _find_events_for_substitution_employee(self):
        tz = self.env.user.tz
        presence_obj = self.env['event.track.presence']
        self.ensure_one()
        date_from = date2str(_convert_to_local_date(self.date_from, tz=tz))
        date_to = date2str(_convert_to_local_date(self.date_to, tz=tz))
        cond = [('partner', '=', self.employee_id.address_home_id.id),
                ('session_date_without_hour', '>=', date_from),
                ('session_date_without_hour', '<=', date_to),
                ('state', '=', 'pending')]
        presences = presence_obj.search(cond)
        events = presences.mapped('event')
        return events
