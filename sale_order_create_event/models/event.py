# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from openerp.addons.event_track_assistant._common import _convert_to_local_date
from dateutil.relativedelta import relativedelta

str2datetime = fields.Datetime.from_string
str2date = fields.Date.from_string


class EventEvent(models.Model):
    _inherit = 'event.event'

    def _compute_event_tasks(self):
        task_obj = self.env['project.task']
        for event in self:
            cond = [('event_id', '=', event.id)]
            tasks = task_obj.search(cond)
            event.my_task_ids = [(6, 0, tasks.ids)]

    @api.depends('my_task_ids')
    def _count_tasks(self):
        for event in self:
            event.count_tasks = len(event.my_task_ids)

    def _compute_count_schedule(self):
        for event in self.filtered(lambda x: x.sale_order and
                                   x.sale_order.project_id):
            event.count_schedule = len(
                event.sale_order.project_id.working_hours)

    my_task_ids = fields.One2many(
        comodel_name='project.task', compute='_compute_event_tasks',
        string='Tasks', oldname='tasks')
    sale_order = fields.Many2one(
        comodel_name='sale.order', string='Sale Order')
    sale_order_line = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Order Line')
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account',
        related='project_id.analytic_account_id', store=True)
    count_schedule = fields.Integer(
        string='Schedule', compute='_compute_count_schedule')
    notes = fields.Text(string='Notes')

    @api.multi
    def unlink(self):
        for event in self:
            if event.sale_order and event.sale_order.state != 'cancel':
                raise exceptions.Warning(
                    _("You can not delete the event '%s', because the sale"
                      " order '%s', is not in cancel status ") %
                    (event.name, event.sale_order.name))
            if len(event.registration_ids) > 0:
                raise exceptions.Warning(
                    _("You can not delete the event '%s', because has people"
                      " registered") % (event.name))
            if event.sale_order and event.sale_order.project_by_task == 'yes':
                event._delete_event_information_by_task()
            else:
                event.my_task_ids.unlink()
            event.track_ids.unlink()
        return super(EventEvent, self).unlink()

    def _create_event_from_sale(self, by_task, sale, line=False):
        project_obj = self.env['project.project']
        cond = [('analytic_account_id', '=', sale.project_id.id)]
        project = project_obj.search(cond, limit=1)
        name = sale.name
        if by_task:
            name = u'{}. {}'.format(name, line.name)
        event_vals = sale._prepare_event_data(sale, line, name, project)
        products = sale.mapped(
            'order_line.product_id.ticket_event_product_ids')
        if by_task:
            event_vals['sale_order_line'] = line.id
            products = line.mapped('product_id.ticket_event_product_ids')
        for product in products:
            if 'event_ticket_ids' not in event_vals:
                event_vals['event_ticket_ids'] = []
            event_vals['event_ticket_ids'].append((0, 0, {
                'name': product.name,
                'product_id': product.id,
                'price': product.lst_price,
            }))
        event = self.with_context(
            sale_order_create_event=True).create(event_vals)
        if line:
            line.event_id = event
        return event

    @api.model
    def _default_tickets(self):
        res = super(EventEvent, self)._default_tickets()
        for line_dict in res:
            try:
                if line_dict.get('product_id', False) ==\
                        self.env.ref('event_sale.product_product_event').id:
                    res.remove(line_dict)
            except Exception:
                pass
        return res

    def _delete_event_information_by_task(self):
        for task in self.my_task_ids:
            project = False
            if task.project_id:
                project = task.project_id
                account = project.analytic_account_id
            task.unlink()
            if project:
                project.unlink()
                account.unlink()

    def _update_event_dates(
            self, old_date, new_days, new_date, begin=False, end=False):
        project_obj = self.env['project.project']
        tz = self.env.user.tz
        vals = {}
        if begin:
            vals['date_begin'] =\
                str2datetime(self.date_begin).replace(
                    year=new_date.year, month=new_date.month, day=new_date.day)
        elif end:
            vals['date_end'] =\
                str2datetime(self.date_end).replace(
                    year=new_date.year, month=new_date.month, day=new_date.day)
        self.with_context(
            sale_order_create_event=True, no_recalculate=True).write(vals)
        if begin:
            registrations = self.registration_ids.filtered(
                lambda x: str2datetime(x.date_start).date() ==
                old_date)
            for registration in registrations:
                registration.date_start =\
                    str2datetime(registration.date_start).replace(
                        year=new_date.year, month=new_date.month,
                        day=new_date.day)
            self.my_task_ids.write({'date_start': self.date_begin})
            new_date = _convert_to_local_date(self.date_begin, tz=tz).date()
            projects = self.mapped('my_task_ids.project_id')
            projects.write({'date_start': new_date})
            accounts = projects.mapped('analytic_account_id')
            accounts.write({'date_start': new_date})
        if end:
            registrations = self.registration_ids.filtered(
                lambda x: str2datetime(x.date_end).date() ==
                old_date)
            for registration in registrations:
                registration.date_end =\
                    str2datetime(registration.date_end).replace(
                        year=new_date.year, month=new_date.month,
                        day=new_date.day)
            self.my_task_ids.write({'date_end': self.date_end})
            new_date = _convert_to_local_date(self.date_end, tz=tz).date()
            projects = self.mapped('my_task_ids.project_id')
            projects.write({'date': new_date})
            accounts = projects.mapped('analytic_account_id')
            accounts.write({'date': new_date})
        if self.sale_order and self.sale_order.project_id and (begin or end):
            if begin:
                self.sale_order.project_id.date_start = new_date
            if end:
                self.sale_order.project_id.date = new_date
            cond = [('analytic_account_id', '=',
                     self.sale_order.project_id.id)]
            project = project_obj.search(cond, limit=1)
            if project and begin:
                project.date_start = new_date
            if project and end:
                project.date = new_date

    @api.multi
    def show_schedule_from_event(self):
        self.ensure_one()
        if self.count_schedule > 0:
            return {'name': _('Schedule'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'resource.calendar',
                    'domain': [('id', '=',
                                self.sale_order.project_id.working_hours.id)]}


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.depends('tasks')
    def _compute_task_id(self):
        for track in self:
            track.task_id = False
            if track.tasks:
                track.task_id = track.tasks[0].id

    tasks = fields.Many2many(
        comodel_name="project.task", relation="task_session_project_relation",
        column1="track_id", column2="task_id", copy=True, string="Tasks")
    task_id = fields.Many2one(
        comodel_name="project.task", compute='_compute_task_id',
        copy=True, string="Task", store=True)

    def _change_session_date(self, new_days):
        event_begin = str2date(self.event_id.date_begin)
        event_end = str2date(self.event_id.date_end)
        new_date = str2date(self.date) + relativedelta(days=new_days)
        new_date_with_hour =\
            str2datetime(self.date) + relativedelta(days=new_days)
        if new_date < event_begin:
            self.event_id._update_event_dates(
                event_begin, new_days, new_date, begin=True)
        if new_date > event_end:
            self.event_id._update_event_dates(
                event_end, new_days, new_date, end=True)
        estimated_date_end =\
            new_date_with_hour + relativedelta(hours=self.duration)
        vals = {'date': new_date_with_hour,
                'session_date': new_date,
                'estimated_date_end': estimated_date_end}
        self.write(vals)


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    @api.depends('session_date', 'session_duration')
    def _compute_estimated_daynightlight_hours(self):
        super(EventTrackPresence,
              self)._compute_estimated_daynightlight_hours()
        for presence in self.filtered('session_duration'):
            start_date = _convert_to_local_date(
                presence.session_date, self.env.user.tz)
            presence.start_hour = '{:%H:%M:%S}'.format(start_date)
            end_date = start_date + relativedelta(
                hours=presence.session_duration)
            presence.end_hour = '{:%H:%M:%S}'.format(end_date)

    start_hour = fields.Char(
        string='Start hour', compute='_compute_estimated_daynightlight_hours',
        store=True)
    end_hour = fields.Char(
        string='End hour', compute='_compute_estimated_daynightlight_hours',
        store=True)
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic account',
        related='event.analytic_account_id', store=True)
    analytic_account_state = fields.Selection(
        string='Analytic account state', store=True,
        related='analytic_account_id.state')
    customer_id = fields.Many2one(
        comodel_name='res.partner', string='Customer',
        related='event.sale_order.partner_id', store=True)
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee',
        related='partner.employee_id', store=True)

    @api.multi
    def button_canceled(self):
        self._delete_hours_in_project_task()
        return super(EventTrackPresence, self).button_canceled()

    @api.multi
    def button_pending(self):
        self._delete_hours_in_project_task()
        return super(EventTrackPresence, self).button_pending()

    @api.multi
    def button_completed(self):
        res = super(EventTrackPresence, self).button_completed()
        self._impute_hours_in_project_task()
        return res

    @api.multi
    def _impute_hours_in_project_task(self):
        for presence in self.filtered(
                lambda x: x.partner.employee_id and x.real_duration):
            work_vals = {'event_id': presence.event.id,
                         'date': presence.session.real_date_end,
                         'task_id': presence.session.tasks[:1].id,
                         'name': presence.session.name,
                         'hours': presence.real_duration,
                         'user_id': presence.partner.employee_id.user_id.id}
            self.env['project.task.work'].create(work_vals)
            try:
                presence.session.stage_id = self.env.ref(
                    'website_event_track.event_track_stage5')
            except Exception:
                continue

    @api.multi
    def _delete_hours_in_project_task(self):
        work_obj = self.env['project.task.work']
        for presence in self.filtered(
                lambda x: x.partner.employee_id and x.real_duration):
            cond = [('event_id', '=', presence.event.id),
                    ('date', '=', presence.session.real_date_end),
                    ('task_id', '=', presence.session.tasks[:1].id),
                    ('user_id', '=', presence.partner.employee_id.user_id.id)]
            work_obj.search(cond, limit=1).unlink()


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.one
    def confirm_registration(self):
        if self.partner_id.pending_receipts:
            raise exceptions.Warning(
                _("%s with pending payment receipts.") %
                self.partner_id.name)
        if self.partner_id.with_incident:
            raise exceptions.Warning(
                _("%s with incidents.") %
                self.partner_id.name)
        super(EventRegistration, self).confirm_registration()
