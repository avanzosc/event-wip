# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def write(self, vals):
        if (self.env.context.get('sale_order_create_event', False) and
                vals.get('date', False)):
            vals.pop('date')
        return super(ProjectProject, self).write(vals)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    def _compute_num_sessions(self):
        for task in self:
            task.num_sessions = len(task.sessions)

    @api.model
    @api.depends('event_id', 'event_id.address_id',
                 'event_id.address_id.street', 'event_id.address_id.street2',
                 'event_id.address_id.zip', 'event_id.address_id.city')
    def _compute_event_address(self):
        partner_obj = self.env['res.partner']
        for task in self.filtered(lambda x: x.event_id):
            task.event_address = ''
            if task.event_id.address_id:
                task.event_address = partner_obj._display_address(
                    task.event_id.address_id)

    @api.model
    @api.depends('project_id', 'project_id.partner_id',
                 'project_id.partner_id.street',
                 'project_id.partner_id.street2', 'project_id.partner_id.zip',
                 'project_id.partner_id.city')
    def _compute_customer_address(self):
        partner_obj = self.env['res.partner']
        for task in self.filtered(lambda x: x.project_id):
            task.customer_address = ''
            if task.project_id.partner_id:
                task.customer_address = partner_obj._display_address(
                    task.project_id.partner_id)

    sessions_partners = fields.Many2many(
        comodel_name="res.partner", relation="task_session_partners_relation",
        column1="session_task_id", column2="session_partner_id",
        string="Partners of sessions")
    sessions = fields.Many2many(
        comodel_name="event.track", relation="task_session_project_relation",
        column1="task_id", column2="track_id", copy=False, string="Sessions")
    num_sessions = fields.Integer(
        string='# Session', compute='_compute_num_sessions')
    recurring_service = fields.Boolean(
        string='Recurring Service',
        related='service_project_sale_line.recurring_service')
    january = fields.Boolean(
        string='January', related='service_project_sale_line.january')
    february = fields.Boolean(
        string='February', related='service_project_sale_line.february')
    march = fields.Boolean(
        string='March', related='service_project_sale_line.march')
    april = fields.Boolean(
        string='April', related='service_project_sale_line.april')
    may = fields.Boolean(
        string='May', related='service_project_sale_line.may')
    june = fields.Boolean(
        string='June', related='service_project_sale_line.june')
    july = fields.Boolean(
        string='July', related='service_project_sale_line.july')
    august = fields.Boolean(
        string='August', related='service_project_sale_line.august')
    september = fields.Boolean(
        string='September', related='service_project_sale_line.september')
    october = fields.Boolean(
        string='October', related='service_project_sale_line.october')
    november = fields.Boolean(
        string='November', related='service_project_sale_line.november')
    december = fields.Boolean(
        string='December', related='service_project_sale_line.december')
    week1 = fields.Boolean(
        string='Week 1', related='service_project_sale_line.week1')
    week2 = fields.Boolean(
        string='Week 2', related='service_project_sale_line.week2')
    week3 = fields.Boolean(
        string='Week 3', related='service_project_sale_line.week3')
    week4 = fields.Boolean(
        string='Week 4', related='service_project_sale_line.week4')
    week5 = fields.Boolean(
        string='Week 5', related='service_project_sale_line.week5')
    week6 = fields.Boolean(
        string='Week 6', related='service_project_sale_line.week6')
    monday = fields.Boolean(
        string='Monday', related='service_project_sale_line.monday')
    tuesday = fields.Boolean(
        string='Tuesday', related='service_project_sale_line.tuesday')
    wednesday = fields.Boolean(
        string='Wednesday', related='service_project_sale_line.wednesday')
    thursday = fields.Boolean(
        string='Thursday', related='service_project_sale_line.thursday')
    friday = fields.Boolean(
        string='Friday', related='service_project_sale_line.friday')
    saturday = fields.Boolean(
        string='Saturday', related='service_project_sale_line.saturday')
    sunday = fields.Boolean(
        string='Sunday', related='service_project_sale_line.sunday')
    event_address = fields.Char(
        string='Event address', compute='_compute_event_address',
        store=True)
    customer_address = fields.Char(
        string='Customer address', compute='_compute_customer_address',
        store=True)

    def _create_task_from_procurement_service_project(self, procurement):
        task = super(
            ProjectTask,
            self)._create_task_from_procurement_service_project(procurement)
        if task.service_project_sale_line.order_id.project_by_task == 'yes':
            parent_account = task.project_id.analytic_account_id
            code = self.env['ir.sequence'].get('account.analytic.account')
            new_account = self._create_new_account_project_by_task(
                task, parent_account, code)
            cond = [('analytic_account_id', '=', new_account.id)]
            project = self.env['project.project'].search(cond, limit=1)
            task.project_id = project.id
            new_account.date = parent_account.date
            project.date = parent_account.date
            sale_name = task.service_project_sale_line.order_id.name
            if not self.env.context.get('without_sale_name', False):
                parent_account.write({'name': sale_name})
        return task

    def _create_new_account_project_by_task(self, task, parent_account, code):
        vals = {'name': (task.service_project_sale_line.order_id.name + ': ' +
                         task.service_project_sale_line.name),
                'use_tasks': True,
                'type': 'contract',
                'date_start':
                task.project_id.analytic_account_id.date_start or False,
                'date': task.project_id.analytic_account_id.date or False,
                'parent_id': parent_account.id,
                'code': code,
                'partner_id':
                task.project_id.analytic_account_id.partner_id.id}
        return self.env['account.analytic.account'].create(vals)

    @api.multi
    def show_sessions_from_task(self):
        self.ensure_one()
        return {'name': _('Sessions'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form,calendar',
                'view_type': 'form',
                'res_model': 'event.track',
                'domain': [('id', 'in', self.sessions.ids)]}

    @api.multi
    def button_recalculate_sessions(self):
        self.ensure_one()
        self.sessions.unlink()
        num_session = 0
        fec_ini = fields.Date.from_string(self.date_start).replace(day=1)
        num_week = 0 if fec_ini.weekday() == 0 else 1
        month = fec_ini.month
        while fec_ini <= fields.Date.from_string(self.date_end):
            if month != fec_ini.month:
                month = fec_ini.month
                num_week = 0 if fec_ini.weekday() == 0 else 1
            if fec_ini.weekday() == 0:
                num_week += 1
            if fec_ini >= fields.Date.from_string(self.date_start):
                valid = self._validate_event_session_month(self, fec_ini)
                if valid:
                    valid = self._validate_event_session_week(
                        self, num_week)
                if valid:
                    valid = self._validate_event_session_day(self, fec_ini)
                if valid:
                    num_session += 1
                    self._create_session_from_task(
                        self.event_id, num_session, fec_ini)
            fec_ini = fec_ini + relativedelta(days=+1)

    def _validate_event_session_month(self, line, fec_ini):
        valid = False
        month = fec_ini.month
        if ((line.january and month == 1) or
            (line.february and month == 2) or
            (line.march and month == 3) or
            (line.april and month == 4) or
            (line.may and month == 5) or
            (line.june and month == 6) or
            (line.july and month == 7) or
            (line.august and month == 8) or
            (line.september and month == 9) or
            (line.october and month == 10) or
            (line.november and month == 11) or
                (line.december and month == 12)):
            valid = True
        return valid

    def _validate_event_session_week(self, line, num_week):
        valid = False
        if ((line.week1 and num_week == 1) or
            (line.week2 and num_week == 2) or
            (line.week3 and num_week == 3) or
            (line.week4 and num_week == 4) or
            (line.week5 and num_week == 5) or
                (line.week6 and num_week == 6)):
            valid = True
        return valid

    def _validate_event_session_day(self, line, fec_ini):
        valid = False
        day = fec_ini.weekday()
        if ((line.monday and day == 0) or
            (line.tuesday and day == 1) or
            (line.wednesday and day == 2) or
            (line.thursday and day == 3) or
            (line.friday and day == 4) or
            (line.saturday and day == 5) or
                (line.sunday and day == 6)):
            valid = True
        return valid

    def _create_session_from_task(self, event, num_session, date):
        vals = self._prepare_session_data_from_task(event, num_session, date)
        self.env['event.track'].create(vals)
        duration = sum(self.mapped('sessions.duration'))
        self.planned_hours = duration

    def _prepare_session_data_from_task(self, event, num_session, date):
        new_date = (datetime.strptime(str(date), '%Y-%m-%d') +
                    relativedelta(hours=float(0.0)))
        local = pytz.timezone(self.env.user.tz)
        local_dt = local.localize(new_date, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        duration = (self.service_project_sale_line.product_uom_qty *
                    (self.service_project_sale_line.performance or 1))
        vals = {'name': (_('Session %s for %s') %
                         (str(num_session),
                          self.service_project_sale_line.name)),
                'event_id': event.id,
                'date': utc_dt,
                'duration': duration,
                'tasks': [(4, self.id)]}
        return vals
