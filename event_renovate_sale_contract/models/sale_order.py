# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_new_sale_contract_information(self, origin_sale):
        super(SaleOrder,
              self)._update_new_sale_contract_information(origin_sale)
        self.project_id.sale = self
