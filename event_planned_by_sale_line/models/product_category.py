# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    punctual_service = fields.Boolean(
        string='Punctual service', default=False)
