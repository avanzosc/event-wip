# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class WizEventConfirmAssistant(models.TransientModel):
    _inherit = 'wiz.event.confirm.assistant'

    def _select_event_registrations(self, event):
        active_state = self.env.ref('hr_contract_stages.stage_contract3')
        registrations = super(
            WizEventConfirmAssistant, self)._select_event_registrations(event)
        if not registrations:
            return registrations
        regis = registrations.filtered(
            lambda x: x.contract_stage and
            x.contract_stage.id != active_state.id)
        return regis
