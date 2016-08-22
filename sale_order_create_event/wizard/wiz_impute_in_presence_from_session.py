# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class WizImputeInPresenceFromSession(models.TransientModel):
    _inherit = 'wiz.impute.in.presence.from.session'

    @api.multi
    def button_impute_hours(self):
        work_obj = self.env['project.task.work']
        res = super(WizImputeInPresenceFromSession, self).button_impute_hours()
        for line in self.mapped('lines').filtered(
                lambda x: x.partner.employee_id and x.hours):
            work_vals = {'event_id': line.session.event_id.id,
                         'date': line.session.real_date_end,
                         'task_id': line.session.tasks[:1].id,
                         'name': line.session.name,
                         'hours': line.hours,
                         'user_id': line.partner.employee_id.user_id.id}
            work_obj.create(work_vals)
            line.session.stage_id = self.env.ref(
                'website_event_track.event_track_stage5').id
        return res
