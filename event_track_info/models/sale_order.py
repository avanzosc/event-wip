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
        data = training_plan_obj._search_product_training_plan(
            product, num_session)
        if data:
            if data.get('name', False):
                name = u'{} {} - {}'.format(
                    _('Session'), num_session, data.get('name'))
                res['name'] = name
            if data.get('url', False):
                res['url'] = data.get('url')
            if data.get('html_info', False):
                res['description'] = data.get('html_info')
            if data.get('planification', False):
                res['planification'] = data.get('planification')
            if data.get('resolution', False):
                res['resolution'] = data.get('resolution')
        return res
