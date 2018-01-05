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
            treated_tasks = self.env['project.task']
            tasks = self.env['project.task']
            for date in dates:
                sessions = event._take_sessions_to_date(date)
                min_session = min(sessions, key=lambda x: x.id)
                duration = min_session.duration
                task = min_session.tasks
                name = task[0].name
                description = task[0].description
                if task:
                    if task[0] not in treated_tasks:
                        treated_tasks += task[0]
                others_sessions = sessions.filtered(
                    lambda x: x.id != min_session.id).sorted(
                    key=lambda e: e.id)
                for other_session in others_sessions:
                    duration += other_session.duration
                    if other_session.tasks:
                        if (other_session.tasks[0] not in tasks and
                            other_session.tasks[0] not in treated_tasks and
                                other_session.tasks[0] != task):
                            tasks += other_session.tasks[0]
                        if other_session.tasks[0].name not in name:
                            name = u'{} - {}'.format(
                                name, other_session.tasks[0].name)
                            description = u'{}\n{}'.format(
                                description,
                                other_session.tasks[0].description)
                    for presence in other_session.presences:
                        p = min_session.presences.filtered(
                            lambda x: x.partner == presence.partner)
                        if not p:
                            presence.write({'session': min_session.id})
                        else:
                            p.write({'real_duration': (
                                p.real_duration + presence.real_duration)})
                            presence.unlink()
                task[0].write({'name': name, 'description': description})
                others_sessions.unlink()
                min_session.write({'name': name,
                                   'duration': duration})
            if tasks:
                for t in tasks.filtered(lambda x: x.id not in
                                        treated_tasks.ids):
                    cond = [('task_id', '=', t.id)]
                    works = work_obj.search(cond)
                    if works:
                        works.write({'task_id': task.id})
                    t.unlink()

    def _take_sessions_to_date(self, date):
        sessions = self.track_ids.filtered(lambda x: x.session_date == date)
        return sessions
