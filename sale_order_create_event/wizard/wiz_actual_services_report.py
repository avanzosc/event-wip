# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api


class WizActualServicesReport(models.TransientModel):
    _name = 'wiz.actual.services.report'

    from_date = fields.Date(string='From date', required=True)
    to_date = fields.Date(string='To date', required=True)

    @api.multi
    def show_employee_actual_services(self):
        self.ensure_one()
        self.env['event.track.presence.report'].with_context(
            employee_id=self.env.context.get('active_id'),
            from_date=self.from_date,
            to_date=self.to_date).presence_analysis_from_employee()
        return {'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'event.track.presence.report',
                'type': 'ir.actions.act_window'}
