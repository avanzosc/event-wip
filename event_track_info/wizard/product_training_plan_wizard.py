# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class ProductTrainingPlanWizard(models.TransientModel):
    _name = 'product.training.plan.wizard'

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True,
        domain=[('recurring_service', '=', True)])

    @api.multi
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
                data = plan_obj._search_product_training_plan(
                    self.product_id, num_session)
                if data:
                    vals = {'name':  u'{} {} - {}'.format(
                        _('Session'), num_session, data.get('name'))}
                    if data.get('url', False):
                        vals['url'] = u'{}\n{}'.format(
                            track.url or '', data.get('url'))
                    if data.get('planification', False):
                        vals['planification'] = u'{}\n{}'.format(
                            track.planification or '',
                            data.get('planification'))
                    if data.get('resolution', False):
                        vals['resolution'] = u'{}\n{}'.format(
                            track.resolution or '', data.get('resolution'))
                    if data.get('html_info', False):
                        vals['description'] = u'{}\n{}'.format(
                            track.description or '', data.get('html_info'))
                    track.write(vals)
