# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import calendar


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _cron_recurring_create_invoice(self):
        account_obj = self.env['account.analytic.account']
        cond = [('recurring_next_date', '<=', fields.Date.context_today(self)),
                ('state', '=', 'open'),
                ('recurring_invoices', '=', True),
                ('type', '=', 'contract'),
                ('recurring_rule_type', '=', 'monthly'),
                ('sale', '!=', False)]
        accounts = account_obj.search(cond).filtered(
            lambda x: x.sale.payer == 'school')
        for account in accounts:
            fec_ini, fec_end = account._calculate_fec_ini_end()
            lines = account.recurring_invoice_line_ids.filtered(
                lambda x: x.event_id)
            lines._calculate_qty_in_analytic_invoice_line(fec_ini, fec_end)
        return super(AccountAnalyticAccount,
                     self)._cron_recurring_create_invoice()

    def _calculate_fec_ini_end(self):
        date = fields.Date.from_string(self.recurring_next_date)
        if date.month > 9:
            fec_ini = "{}-{}-01".format(date.year, date.month)
            fec_end = "{}-{}-{}".format(
                date.year, date.month, calendar.monthrange(date.year,
                                                           date.month)[1])
        else:
            fec_ini = "{}-0{}-01".format(date.year, date.month)
            fec_end = "{}-0{}-{}".format(
                date.year, date.month, calendar.monthrange(date.year,
                                                           date.month)[1])
        if self.recurring_interval > 1:
            fec_ini = fields.Date.to_string(
                fec_ini + relativedelta(months=self.recurring_interval - 1))
        return fec_ini, fec_end


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    event_id = fields.Many2one(
        comodel_name='event.event', string='Event')

    def _calculate_qty_in_analytic_invoice_line(self, fec_ini, fec_end):
        for line in self:
            count = len(line.event_id.no_employee_registration_ids.filtered(
                lambda x: x.state == 'open' and
                ((fec_end >= x.date_start and fec_end <= x.date_end) or
                 (fec_ini <= x.date_end and fec_ini >= x.date_start))))
            line.quantity = count
