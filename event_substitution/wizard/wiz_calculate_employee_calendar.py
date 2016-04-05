# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, _


class WizCalculateEmployeeCalendar(models.TransientModel):
    _inherit = 'wiz.calculate.employee.calendar'

    @api.multi
    def button_calculate_employee_calendar(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.substitution']
        line_vals = []
        super(WizCalculateEmployeeCalendar,
              self).button_calculate_employee_calendar()
        if self.validate_ausence:
            events = self.ausence.find_events_for_substitution_employee()
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
