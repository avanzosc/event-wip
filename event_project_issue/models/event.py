# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.multi
    def _count_event_issues(self):
        for event in self:
            event.count_issues = len(event.issue_ids)

    issue_ids = fields.One2many(
        comodel_name='project.issue', inverse_name='event_id', string='Issues')
    count_issues = fields.Integer(
        string='Issues', compute='_count_event_issues')

    @api.multi
    def show_event_issues(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['search_default_event'] = self.id
        context['default_event'] = self.id
        context['default_name'] = self.name
        return {'name': _('Event issues'),
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form,calendar,graph',
                'view_type': 'form',
                'res_model': 'project.issue',
                'domain': [('id', 'in', self.issue_ids.ids)],
                'context': context}


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.multi
    def _count_session_issues(self):
        for session in self:
            session.count_issues = len(session.issue_ids)

    issue_ids = fields.One2many(
        comodel_name='project.issue', inverse_name='session_id',
        string='Issues')
    count_issues = fields.Integer(
        string='Issues', compute='_count_session_issues')

    @api.multi
    def show_session_issues(self):
        self.ensure_one()
        context = self.env.context.copy()
        context['search_default_session'] = self.id
        context['default_session'] = self.id
        context['default_name'] = self.name
        return {'name': _('Session issues'),
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form,calendar,graph',
                'view_type': 'form',
                'res_model': 'project.issue',
                'domain': [('id', 'in', self.issue_ids.ids)],
                'context': context}
