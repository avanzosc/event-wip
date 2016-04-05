# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def button_recalculate_sessions(self):
        self.ensure_one()
        super(ProjectTask, self).button_recalculate_sessions()
        self.event_id._put_festives_in_sesions_from_sale_contract(
            self.event_id.sale_order.project_id.festive_calendars)
