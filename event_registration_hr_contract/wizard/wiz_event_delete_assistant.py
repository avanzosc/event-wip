# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class WizEventDeleteAssistant(models.TransientModel):
    _inherit = 'wiz.event.delete.assistant'

    employee = fields.Many2one(
        'hr.employee', related='partner.employee', string='Employee')

    def _cancel_presences(self):
        presences = super(WizEventDeleteAssistant, self)._cancel_presences()
        if self.employee:
            for presence in presences:
                presence._update_employee_calendar_days(
                    contract=False, cancel_presence=True)
        return presences
