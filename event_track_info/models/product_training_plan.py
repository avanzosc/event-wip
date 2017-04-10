# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models


class ProductTrainingPlan(models.Model):
    _inherit = 'product.training.plan'

    def _search_product_training_plan(self, product, num_session):
        data = {}
        cond = [('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', '=', False),
                ('sequence', '=', num_session)]
        data = self._catch_training_plan_information(
            data, self.search(cond))
        cond = [('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', '=', product.id),
                ('sequence', '=', num_session)]
        data = self._catch_training_plan_information(
            data, self.search(cond))
        return data

    def _catch_training_plan_information(self, data, trainings):
        for training in trainings:
            plan = training.training_plan_id
            if data.get('name', False):
                if plan.name not in data.get('name'):
                    data['name'] = u'{}\n\n{}'.format(
                        data.get('name'), plan.name)
            else:
                data['name'] = training.training_plan_id.name
            data['url'] = (data.get('url', False) and u'{}\n\n{}'.format(
                data.get('url'), plan.url) or plan.url)
            data['html_info'] = (
                data.get('html_info', False) and u'{}\n\n{}'.format(
                    data.get('html_info'), plan.html_info) or plan.html_info)
            data['planification'] = (
                data.get('planification', False) and u'{}\n\n{}'.format(
                    data.get('planification'),
                    plan.planification) or plan.planification)
            data['resolution'] = (
                data.get('resolution', False) and u'{}\n\n{}'.format(
                    data.get('resolution'),
                    plan.resolution) or plan.resolution)
        return data
