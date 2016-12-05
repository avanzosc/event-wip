# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    def _prepare_data_for_account_not_employee(self, event, registration):
        vals = super(
            WizEventAppendAssistant,
            self)._prepare_data_for_account_not_employee(event, registration)
        if event.sale_order.project_by_task == 'no':
            return vals
        vals.update({'recurring_invoices': False,
                     'recurring_interval': 1})
        if event.sale_order.payer == 'student':
            vals['recurring_invoices'] = True
        if event.sale_order.product_category.punctual_service:
            vals['recurring_rule_type'] = 'yearly'
        else:
            vals['recurring_rule_type'] = 'monthly'
        return vals
