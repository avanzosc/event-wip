# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    generated_next_year = fields.Boolean(
        string='Generated Next Year', default=False)

    @api.multi
    def automatic_renovate_contract_event(self):
        sale_orders = self.env['sale.order']
#        date = '{}-12-31'.format(
#            int(fields.Date.from_string(fields.Date.today()).year)-1)
        date = '2021-12-31'
        cond = [('project_id', '!=', False),
                ('project_id.state', '=', 'open'),
                ('project_id.type', '=', 'contract'),
                ('project_id.recurring_invoices', '=', True),
                ('project_id.date', '=', date),
                ('generated_next_year', '=', False)]
        sales = self.search(cond)
        for sale in sales:
            cond = [('sale_order', '=', sale.id)]
            event = self.env['event.event'].search(cond, limit=1)
            if event:
                sale_orders += sale
        for sale in sale_orders:
            try:
                with self.env.cr.savepoint():
                    sale._renovate_sale_and_contract_from_wizard()
                    cond = [('generated_from_sale_order', '=', sale.id),
                            ('order_line', '!=', False)]
                    new_sale = self.env['sale.order'].search(cond, limit=1)
                    new_sale.action_button_confirm()
                    if new_sale.project_id:
                        year = int(fields.Date.from_string(
                            new_sale.project_id.date_start).year)
                        new_sale.project_id.name = u'{} {}'.format(
                            new_sale.project_id.partner_id.name, year)
                        cond = [('analytic_account_id', '=', new_sale.project_id.id)]
                        project = self.env['project.project'].search(cond, limit=1)
                        if project:
                            project.name = new_sale.project_id.name
                    sale.generated_next_year = True
            except Exception:
                continue
