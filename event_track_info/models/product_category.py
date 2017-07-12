# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    training_plan_unique_session = fields.Boolean(
        string='Training plan in each of the sessions of the event',
        help="Checking this option, all training plans will be entered in each"
        " of the sessions of the event.", default=False,)
