# -*- coding: utf-8 -*-
# Copyright 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    @api.multi
    def _merge_event_tracks(self):
        work_obj = self.env['project.task.work']
        for event in self.filtered(lambda x: len(x.track_ids) > 0):
            dates = sorted(set(event.mapped('track_ids.session_date')))
            task = False
            tasks = self.env['project.task']
            for date in dates:
                sessions = event.track_ids.filtered(
                    lambda x: x.session_date == date)
                min_session = min(sessions, key=lambda x: x.id)
                duration = min_session.duration
                name = min_session.name
                task = min_session.tasks
                others_sessions = sessions.filtered(
                    lambda x: x.id != min_session.id).sorted(
                    key=lambda e: e.id)
                for other_session in others_sessions:
                    duration += other_session.duration
                    name = u'{}\n{}'.format(name, other_session.name)
                    if (other_session.tasks and
                        other_session.tasks[0] not in tasks and
                            other_session.tasks[0] != task):
                        tasks += other_session.tasks[0]
                    for presence in other_session.presences:
                        p = min_session.presences.filtered(
                            lambda x: x.partner == presence.partner)
                        if not p:
                            presence.write({'session': min_session.id})
                        else:
                            p.write({'real_duration': (
                                p.real_duration + presence.real_duration)})
                            presence.unlink()
                others_sessions.unlink()
                min_session.write({'name': name,
                                   'duration': duration})
            if tasks:
                name = task.name
                description = task.description
                for t in tasks:
                    name = u'{} - {}'.format(name, t.name)
                    description = u'{}\n{}'.format(description,
                                                   t.description)
                    if t.service_project_sale_line:
                        t.service_project_sale_line.write(
                            {'service_project_task': task.id})
                task.write({'name': name,
                            'description': description})
                cond = [('task_id', 'in', tasks.ids)]
                works = work_obj.search(cond)
                if works:
                    works.write({'task_id': task.id})
                tasks.unlink()
