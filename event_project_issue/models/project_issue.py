# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    event_id = fields.Many2one(
        comodel_name='event.event', string="Event")
    session_id = fields.Many2one(
        comodel_name='event.track', string="Event session")

    @api.onchange('event_id')
    def onchange_event(self):
        event_obj = self.env['event.event']
        if 'default_event_id' in self.env.context:
            event = event_obj.browse(self.env.context.get('default_event_id'))
        else:
            event = self.event_id
        if event and event.sale_order:
            if (event.sale_order.project_by_task == 'yes' and
                    event.my_task_ids):
                self.task_id = event.my_task_ids[0].id
                self.project_id = event.my_task_ids[0].project_id.id
            elif event.sale_order.project_by_task == 'no':
                self.project_id = event.project_id.id

    @api.onchange('session_id')
    def onchange_session(self):
        session_obj = self.env['event.track']
        if 'default_session_id' in self.env.context:
            session = session_obj.browse(
                self.env.context.get('default_session_id'))
        else:
            session = self.session_id
        if session:
            self.event_id = session.event_id.id
            self.task_id = session.tasks[:1]
            self.project_id = session.tasks[:1].project_id
