# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class ProductTrainingPlanWizard(models.TransientModel):
    _name = 'product.training.plan.wizard'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True,
        domain=[('recurring_service', '=', True)])

    @api.one
    def put_training_plan_in_sessions(self):
        plan_obj = self.env['product.training.plan']
        event = self.env['event.event'].browse(
            self.env.context.get('active_id'))
        dates = sorted(set(event.mapped('track_ids.session_date')))
        num_session = 0
        for date in dates:
            num_session += 1
            tracks = event.track_ids.filtered(lambda x: x.session_date == date)
            for track in tracks:
                training = plan_obj._search_product_training_plan(
                    self.product_id, num_session)
                if training:
                    vals = {'name':  u'{} {} - {}'.format(
                        _('Session'), num_session,
                        training.training_plan_id.name)}
                    if training.training_plan_id.url:
                        vals['url'] = u'{}\n{}'.format(
                            track.url, training.training_plan_id.url)
                    if training.training_plan_id.planification:
                        vals['planification'] = u'{}\n{}'.format(
                            track.planification,
                            training.training_plan_id.planification)
                    if training.training_plan_id.resolution:
                        vals['resolution'] = u'{}\n{}'.format(
                            track.resolution,
                            training.training_plan_id.resolution)
                    if training.training_plan_id.html_info:
                        vals['description'] = u'{}\n{}'.format(
                            track.description,
                            training.training_plan_id.html_info)
                    track.write(vals)
