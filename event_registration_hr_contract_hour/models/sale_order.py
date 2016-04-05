# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        project_obj = self.env['project.project']
        event_obj = self.env['event.event']
        for sale in self:
            cond = [('analytic_account_id', '=', sale.project_id.id)]
            project = project_obj.search(cond, limit=1)
            cond = [('project_id', '=', project.id)]
            events = event_obj.search(cond)
            for event in events:
                for track in event.track_ids:
                    f = fields.Datetime.from_string(track.session_date).date()
                    day = f.weekday()
                    if day == 6:
                        track.type_hour = self.env.ref(
                            'sale_order_create_event_hour.type_hour_sunday').id
        res = super(SaleOrder, self).action_button_confirm()
        return res
