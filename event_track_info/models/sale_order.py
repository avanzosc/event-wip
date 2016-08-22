# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_session_data_from_sale_line(
            self, event, num_session, line, date):
        res = super(SaleOrder, self)._prepare_session_data_from_sale_line(
            event, num_session, line, date)
        template = self.env['product.event.track.template'].search([
            ('product_id', '=', line.product_id.id),
            ('sequence', '=', num_session)
        ], limit=1)
        if template:
            name = u'{} {}: {}'.format(
                _('Session'), num_session, template.name)
            res.update({
                'name': name,
                'url': template.url,
                'description': template.html_info,
                'planification': template.planification,
                'resolution': template.resolution
            })
        return res
