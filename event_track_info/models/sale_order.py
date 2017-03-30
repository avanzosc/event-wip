# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_session_data_from_sale_line(
            self, event, num_session, line, date):
        training_plan_obj = self.env['product.training.plan']
        res = super(SaleOrder, self)._prepare_session_data_from_sale_line(
            event, num_session, line, date)
        product = line.product_id
        training = training_plan_obj._search_product_training_plan(
            product, num_session)
        if training:
            name = u'{} {} - {}'.format(
                _('Session'), num_session, training.training_plan_id.name)
            res.update({
                'name': name,
                'url': training.training_plan_id.url,
                'description': training.training_plan_id.html_info,
                'planification': training.training_plan_id.planification,
                'resolution': training.training_plan_id.resolution
            })
        return res
