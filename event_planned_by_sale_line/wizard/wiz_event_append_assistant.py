# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models
import calendar


class WizEventAppendAssistant(models.TransientModel):
    _inherit = 'wiz.event.append.assistant'

    def _prepare_data_for_account_not_employee(self, event, registration):
        vals = super(
            WizEventAppendAssistant,
            self)._prepare_data_for_account_not_employee(event, registration)
        if event.sale_order.project_by_task == 'no':
            return vals
        if event.sale_order.payer == 'student':
            vals['recurring_invoices'] = True
        else:
            vals['recurring_invoices'] = False
        if event.sale_order.product_category.punctual_service:
            vals.update({'recurring_interval': 1,
                         'recurring_rule_type': 'yearly',
                         'recurring_next_date':
                         event.sale_order_line.start_date})
        else:
            date = fields.Date.from_string(event.sale_order_line.start_date)
            recurring_next_date = date.replace(
                day=calendar.monthrange(date.year, date.month)[1])
            vals.update({'recurring_next_date': recurring_next_date,
                         'recurring_interval': 1,
                         'recurring_rule_type': 'monthly'})
        return vals
