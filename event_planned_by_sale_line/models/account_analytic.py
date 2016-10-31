# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import calendar

str2datetime = fields.Datetime.from_string
datetime2str = fields.Datetime.to_string


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def _prepare_invoice_line(self, line, fiscal_position):
        values = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, fiscal_position)
        if line.analytic_account_id.sale.payer == 'school':
            quantity = line._calculate_qty_in_analytic_invoice_line()
            values.update({
                'quantity': quantity,
            })
        return values

    def _calculate_fec_ini_end(self, interval=0):
        date = str2datetime(self.recurring_next_date)
        date += relativedelta(months=interval)
        start_date = date.replace(day=1, hour=0, minute=0, second=0)
        end_date = date.replace(
            day=calendar.monthrange(date.year, date.month)[1],
            hour=23, minute=59, second=59)
        start_date = datetime2str(start_date)
        end_date = datetime2str(end_date)
        return start_date, end_date


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    event_id = fields.Many2one(
        comodel_name='event.event', string='Event')

    @api.multi
    def _calculate_qty_in_analytic_invoice_line(self):
        self.ensure_one()
        count = 0
        for interval in range(0, self.analytic_account_id.recurring_interval):
            start_date, end_date =\
                self.analytic_account_id._calculate_fec_ini_end(interval)
            count += len(self.event_id.no_employee_registration_ids.filtered(
                lambda x: x.state == 'open' and
                ((end_date >= x.date_start and end_date <= x.date_end) or
                 (start_date <= x.date_end and start_date >= x.date_start))))
        return count
