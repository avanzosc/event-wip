# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, exceptions, _


class CrmMakeSale(models.TransientModel):
    _inherit = 'crm.make.sale'

    product_category = fields.Many2one(
        comodel_name='product.category', string='Product category',
        required=True)
    payer = fields.Selection(
        [('school', 'School'),
         ('student', 'Student')], string='Payer', required=True)

    @api.multi
    def makeOrder(self):
        lead_obj = self.env['crm.lead']
        self.ensure_one()
        if self.env.context.get('active_ids', False):
            if len(self.env.context.get('active_ids')) > 1:
                raise exceptions.Warning(
                    _('You can only convert to quotation a unique'
                      ' opportunity'))
        my_context = self.env.context.copy()
        my_context.update({'product_category': self.product_category.id,
                           'payer': self.payer})
        res = super(CrmMakeSale, self.with_context(my_context)).makeOrder()
        if 'res_id' in res:
            lead = lead_obj.browse(self.env.context.get('active_id'))
            lead.write({'sale_order': res.get('res_id')})
        return res
