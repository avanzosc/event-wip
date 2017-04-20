# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
from openerp.tools import config
import calendar


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_category = fields.Many2one(
        comodel_name='product.category', string='Product Category')
    payer = fields.Selection(
        selection=[('school', 'School'), ('student', 'Student')],
        string='Payer', default='student')
    only_products_category = fields.Boolean(
        string='Select in sale order lines ONLY products from this category',
        related='product_category.only_products_category')

    @api.onchange('product_category')
    def onchange_product_category(self):
        if self.mapped('order_line'):
            self.product_category =\
                self.mapped('order_line.product_category')[:1]
            return {'warning':
                    {'title': _('Product Category Change'),
                     'message': _('You can not change category if there are'
                                  ' lines created.')}}

    @api.multi
    def onchange_template_id(self, template_id, partner=False,
                             fiscal_position=False, product_category=False):
        product_obj = self.env['product.product']
        template_obj = self.env['product.template']
        if template_id and not product_category:
            return {'value': {'template_id': False},
                    'warning': {'title': _('Error in product category'),
                                'message':
                                _('You must introduce the product category')}}
        res = super(SaleOrder, self).onchange_template_id(
            template_id, partner=partner, fiscal_position=fiscal_position)
        lines = [(6, 0, [])]
        if isinstance(res, dict) and 'value' in res:
            value = res.get('value')
            order_lines = []
            if ('order_line' in value and value.get('order_line')):
                order_lines = value.get('order_line')
            for line in order_lines:
                if line[0] != 5 and line[0] == 0 and line[1] == 0:
                    if line[2].get('product_id'):
                        product = product_obj.browse(line[2].get('product_id'))
                        if product.categ_id.id == product_category:
                            line[2]['product_category'] = product.categ_id.id
                            lines.append(line)
                    elif line[2].get('product_tmpl_id'):
                        template = template_obj.browse(
                            line[2].get('product_tmpl_id'))
                        if template.categ_id.id == product_category:
                            line[2]['product_category'] = template.categ_id.id
                            lines.append(line)
            res['value']['order_line'] = lines
        return res

    @api.multi
    def action_button_confirm(self):
        for sale in self:
            if any(sale.mapped('order_line.product_id.recurring_service')):
                sale._create_automatic_contract_from_sale()
        res = super(SaleOrder, self).action_button_confirm()
        for sale in self.filtered(
                lambda x: x.project_id and x.project_id.date_start):
            vals = {
                'recurring_invoices': sale.payer == 'school',
                'recurring_interval': 1,
            }
            if sale.product_category.punctual_service:
                vals.update({
                    'recurring_next_date': sale.project_id.date_start,
                    'recurring_rule_type': 'yearly',
                })
            else:
                date = fields.Date.from_string(sale.project_id.date_start)
                recurring_next_date =\
                    date.replace(day=calendar.monthrange(date.year,
                                                         date.month)[1])
                vals.update({
                    'recurring_next_date': recurring_next_date,
                    'recurring_rule_type': 'monthly',
                })
            sale.project_id.write(vals)
            if sale.payer == 'school':
                sale._generate_recurring_invoice_lines()
        return res

    def _create_automatic_contract_from_sale(self):
        account_obj = self.env['account.analytic.account']
        if (config['test_enable'] and
                not self.env.context.get('check_automatic_contract_creation')):
            return True
        for sale in self:
            min_fec = min(sale.mapped('order_line.start_date'))
            max_fec = max(sale.mapped('order_line.end_date'))
            if min_fec and max_fec:
                account_vals = {'sale': sale.id,
                                'partner_id': sale.partner_id.id,
                                'name': sale.name,
                                'use_tasks': True,
                                'date_start': min_fec,
                                'date': max_fec}
                sale.project_id = account_obj.create(account_vals)

    @api.multi
    def action_cancel(self):
        project_obj = self.env['project.project']
        res = super(SaleOrder, self).action_cancel()
        analytics = self.filtered(
            lambda x: x.project_by_task == 'yes').mapped('project_id')
        projects = project_obj.search([('analytic_account_id', 'in',
                                       analytics.ids)])
        projects.unlink()
        analytics.unlink()
        return res

    def _generate_recurring_invoice_lines(self):
        invoice_line_obj = self.env['account.analytic.invoice.line']
        self.project_id.recurring_invoice_line_ids.unlink()
        for line in self.order_line.filtered(lambda x: x.event_id):
            vals = {'analytic_account_id': self.project_id.id,
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'quantity': 1,
                    'uom_id': line.product_id.uom_id.id,
                    'price_unit': line.price_unit,
                    'event_id': line.event_id.id}
            invoice_line_obj.create(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_category = fields.Many2one(
        comodel_name='product.category', string='Product category')
    only_products_category = fields.Boolean(
        string='Select in sale order lines ONLY products from this category')

    @api.multi
    @api.onchange('only_products_category')
    def onchange_only_products_category(self):
        cond = []
        if self.only_products_category:
            cond = [('categ_id', '=', self.product_category.id)]
        return {'domain': {'product_tmpl_id': cond,
                           'product_id': cond}}

    @api.multi
    def product_id_change(
            self, pricelist, product, qty=0, uom=False, qty_uos=0,
            uos=False, name='', partner_id=False, lang=False, update_tax=True,
            date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        if not product and 'default_product_category' in self.env.context:
            if 'domain' not in res:
                res['domain'] = {}
            if 'product_id' not in res['domain']:
                res['domain']['product_id'] = []
            cond = res['domain']['product_id']
            cond.append(('categ_id', '=',
                         self.env.context.get('default_product_category')))
            res['domain']['product_id'] = cond
        return res

    @api.onchange('start_date', 'end_date')
    def onchange_start_end_date(self):
        self.ensure_one()
        if self.start_date and self.end_date:
            fec_ini = fields.Date.from_string(self.start_date)
            fec_fin = fields.Date.from_string(self.end_date)
            months = list(range(fec_ini.month, fec_fin.month + 1))
            self.january = 1 in months
            self.february = 2 in months
            self.march = 3 in months
            self.april = 4 in months
            self.may = 5 in months
            self.june = 6 in months
            self.july = 7 in months
            self.august = 8 in months
            self.september = 9 in months
            self.october = 10 in months
            self.november = 11 in months
            self.december = 12 in months
