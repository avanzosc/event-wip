# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _duplicate_sale_order_from_contract(self, origin_sale,
                                            origin_contract):
        new_sale = super(
            AccountAnalyticAccount, self)._duplicate_sale_order_from_contract(
            origin_sale, origin_contract)
        new_sale.project_id.sale = new_sale
        return new_sale
