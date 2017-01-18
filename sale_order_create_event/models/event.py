# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from dateutil.relativedelta import relativedelta


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

    my_task_ids = fields.One2many(
        comodel_name='project.task', compute='_compute_event_tasks',
        string='Tasks', oldname='tasks')
    sale_order = fields.Many2one(
        comodel_name='sale.order', string='Sale Order')
    sale_order_line = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Order Line')

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
            except:
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
        event_obj = self.env['event.event']
        vals = {}
        if begin:
            vals['date_begin'] = (
                fields.Datetime.from_string(
                    self.date_begin).replace(year=new_date.year,
                                             month=new_date.month,
                                             day=new_date.day))
        elif end:
            vals['date_end'] = (
                fields.Datetime.from_string(
                    self.date_end).replace(year=new_date.year,
                                           month=new_date.month,
                                           day=new_date.day))
        self.with_context(
            sale_order_create_event=True, no_recalculate=True).write(vals)
        if begin:
            registrations = self.registration_ids.filtered(
                lambda x: fields.Datetime.from_string(x.date_start).date() ==
                old_date)
            for registration in registrations:
                registration.date_start = (
                    fields.Datetime.from_string(
                        registration.date_start).replace(year=new_date.year,
                                                         month=new_date.month,
                                                         day=new_date.day))
            self.my_task_ids.write({'date_start': self.date_begin})
            new_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_begin).date()
            projects = self.mapped('my_task_ids.project_id')
            projects.write({'date_start': new_date})
            accounts = projects.mapped('analytic_account_id')
            accounts.write({'date_start': new_date})
        if end:
            registrations = self.registration_ids.filtered(
                lambda x: fields.Datetime.from_string(x.date_end).date() ==
                old_date)
            for registration in registrations:
                registration.date_end = (
                    fields.Datetime.from_string(
                        registration.date_end).replace(year=new_date.year,
                                                       month=new_date.month,
                                                       day=new_date.day))
            self.my_task_ids.write({'date_end': self.date_end})
            new_date = event_obj._convert_date_to_local_format_with_hour(
                self.date_end).date()
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


class EventTrack(models.Model):
    _inherit = 'event.track'

    tasks = fields.Many2many(
        comodel_name="project.task", relation="task_session_project_relation",
        column1="track_id", column2="task_id", copy=True, string="Tasks")

    def _change_session_date(self, new_days):
        event_begin = fields.Date.from_string(self.event_id.date_begin)
        event_end = fields.Date.from_string(self.event_id.date_end)
        new_date = (fields.Date.from_string(self.date) +
                    relativedelta(days=new_days))
        new_date_with_hour = (fields.Datetime.from_string(self.date) +
                              relativedelta(days=new_days))
        if new_date < event_begin:
            self.event_id._update_event_dates(event_begin, new_days,
                                              new_date, begin=True)
        if new_date > event_end:
            self.event_id._update_event_dates(event_end, new_days,
                                              new_date, end=True)
        estimated_date_end = (new_date_with_hour +
                              relativedelta(hours=self.duration))
        vals = {'date': new_date_with_hour,
                'session_date': new_date,
                'estimated_date_end': estimated_date_end}
        self.write(vals)


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        date_from = self.date_start or self.event_id.date_begin
        date_to = self.date_end or self.event_id.date_end
        sessions = self.event_id.track_ids.filtered(
            lambda x: x.date >= date_from and x.date <= date_to and x.date)
        tasks = sessions.mapped('tasks')
        wiz_vals.update({
            'permitted_tasks': [(6, 0, tasks.ids)],
            'tasks': [(6, 0, tasks.ids)],
        })
        return wiz_vals
