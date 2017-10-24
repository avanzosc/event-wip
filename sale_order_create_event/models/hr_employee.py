# -*- coding: utf-8 -*-
# © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def button_show_employee_services(self):
        self.env['event.track.presence.report'].with_context(
            employee_id=self.id).presence_analysis_from_employee()
        return {'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'event.track.presence.report',
                'type': 'ir.actions.act_window'}
