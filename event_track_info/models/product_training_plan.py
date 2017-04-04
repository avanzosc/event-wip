# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class ProductTrainingPlan(models.Model):
    _inherit = 'product.training.plan'

    def _search_product_training_plan(self, product, num_session):
        training = self.search([
            '|', '&', ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('product_id', '=', False), ('product_id', '=', product.id),
            ('sequence', '=', num_session)], limit=1)
        return training
