# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_order = fields.Many2one(
        comodel_name='sale.order', string='Sale order', readonly=True)
