# -*- coding: utf-8 -*-
# Copyright © 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class WizEventRegistrationConfirm(models.TransientModel):
    _inherit = 'wiz.event.registration.confirm'

    def _prepare_data_confirm_assistant(self, reg):
        res = super(WizEventRegistrationConfirm,
                    self)._prepare_data_confirm_assistant(reg)
        res['contract'] = reg.contract.id or False
        return res
