# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        template_obj = self.env['product.event.track.template']
        res = super(SaleOrder, self).action_button_confirm()
        for sale in self:
            for line in sale.order_line:
                if line.event_id and line.product_id.event_track_template_ids:
                    sequence = 0
                    for track in line.event_id.track_ids:
                        sequence += 1
                        cond = [('product_id', '=', line.product_id.id),
                                ('sequence', '=', sequence)]
                        template = template_obj.search(cond, limit=1)
                        if template:
                            name = "{} {}: {}".format(_('Session'), sequence,
                                                      template.name)
                            vals = {'name': name,
                                    'url': template.url,
                                    'description': template.html_info,
                                    'planification': template.planification,
                                    'resolution': template.resolution}
                            track.write(vals)
        return res
