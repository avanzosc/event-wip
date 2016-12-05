# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class WizRegistrationToAnotherEvent(models.TransientModel):
    _inherit = 'wiz.registration.to.another.event'

    def _change_registration_event(self):
        super(WizRegistrationToAnotherEvent, self)._change_registration_event()
        if self.event_registration_id.analytic_account:
            self.event_registration_id.analytic_account.unlink()
