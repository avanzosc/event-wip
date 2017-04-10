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
            if data.get('name', False):
                if training.training_plan_id.name not in data.get('name'):
                    data['name'] = u'{}\n\n{}'.format(
                        data.get('name'), training.training_plan_id.name)
            else:
                data['name'] = training.training_plan_id.name
            if data.get('url', False):
                data['url'] = u'{}\n\n{}'.format(
                    data.get('url'), training.training_plan_id.url)
            else:
                data['url'] = training.training_plan_id.url
            if data.get('html_info', False):
                data['html_info'] = u'{}\n\n{}'.format(
                    data.get('html_info'), training.training_plan_id.html_info)
            else:
                data['html_info'] = training.training_plan_id.html_info
            if data.get('planification', False):
                data['planification'] = u'{}\n\n{}'.format(
                    data.get('planification'),
                    training.training_plan_id.planification)
            else:
                data['planification'] = training.training_plan_id.planification
            if data.get('resolution', False):
                data['resolution'] = u'{}\n\n{}'.format(
                    data.get('resolution'),
                    training.training_plan_id.resolution)
            else:
                data['resolution'] = training.training_plan_id.resolution
        return data
