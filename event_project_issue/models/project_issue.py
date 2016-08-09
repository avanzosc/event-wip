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
        if self.event_id and len(self.event_id.my_task_ids) == 1:
            self.task_id = self.event_id.my_task_ids[0].id
            self.project_id = self.event_id.my_task_ids[0].project_id.id

    @api.onchange('session_id')
    def onchange_session(self):
        if (self.session_id and self.session_id.event_id and
                len(self.session_id.event_id.my_task_ids) == 1):
            event = self.session_id.event_id
            self.event = event.id
            self.task_id = event.my_task_ids[0].id
            self.project_id = event.my_task_ids[0].project_id.id

    @api.model
    def create(self, vals):
        event_obj = self.env['event.event']
        session_obj = self.env['event.track']
        if vals.get('event_id', False):
            event = event_obj.browse(vals.get('event_id'))
            if len(event.my_task_ids) == 1:
                vals.update({'project_id': event.my_task_ids[0].project_id.id,
                             'task_id': event.my_task_ids[0].id})
        if vals.get('session_id', False):
            session = session_obj.browse(vals.get('session_id'))
            if len(session.event_id.my_task_ids) == 1:
                event = session.event_id
                vals.update({'project_id': event.my_task_ids[0].project_id.id,
                             'task_id': event.my_task_ids[0].id})
        return super(ProjectIssue, self).create(vals)
