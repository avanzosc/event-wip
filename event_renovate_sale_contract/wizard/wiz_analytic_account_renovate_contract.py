# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class WizAnalyticAccountRenovateContract(models.TransientModel):
    _inherit = 'wiz.analytic.account.renovate.contract'

    def _search_contracts(self):
        contracts = super(
            WizAnalyticAccountRenovateContract, self)._search_contracts()
        return contracts.filtered(lambda x: not x.sale)
