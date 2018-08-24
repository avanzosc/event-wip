# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api, fields, exceptions, _
from openerp.addons.event_track_assistant._common import _convert_to_utc_date
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_by_task = fields.Selection(
        selection=[('yes', 'Yes'), ('no', 'No')],
        string='Create project by task')
    project_start_date = fields.Date(
        string='Project start date', related='project_id.date_start')
    project_end_date = fields.Date(
        string='Project end date', related='project_id.date')
    project_id = fields.Many2one(
        comodel_name='account.analytic.account', copy=False)

    @api.multi
    def action_button_confirm(self):
        event_obj = self.env['event.event']
        project_obj = self.env['project.project']
        if not self.env.user.tz:
            raise exceptions.Warning(_('User without time zone'))
        if any(self.mapped('order_line.product_id.recurring_service')) and\
                (not self.project_id or not self.project_by_task):
            raise exceptions.Warning(
                _('You must enter the Project / Contract and/or select a '
                  'value for \'Create project by task\''))
        if self.project_id:
            if not self.project_id.date_start:
                raise exceptions.Warning(
                    _('You must enter the start date of the project/contract'))
            if not self.project_id.date:
                raise exceptions.Warning(
                    _('You must enter the end date of the project/contract'))
            self.project_id.sale = self.id
            cond = [('analytic_account_id', '=', self.project_id.id)]
            project = project_obj.search(cond, limit=1)
            if not project:
                raise exceptions.Warning(_('Project/contract without project'))
            cond = [('project_id', '=', project.id)]
            event = event_obj.search(cond)
            if event:
                raise exceptions.Warning(
                    _("The project:  '%s', of sale order,already exist in "
                      "other event. You must create a new project for sale"
                      "order.") % project.name)
        res = super(SaleOrder, self).action_button_confirm()
        self._create_event_and_sessions_from_sale_order()
        return res

    def _create_event_and_sessions_from_sale_order(self):
        event_obj = self.env['event.event']
        for sale in self.filtered('project_id'):
            sale_lines = sale.order_line.filtered(
                lambda x: x.recurring_service)
            if sale_lines and sale.project_by_task == 'no':
                event = event_obj._create_event_from_sale(False, sale)
            for line in sale_lines:
                if sale.project_by_task == 'yes':
                    event = event_obj._create_event_from_sale(True, sale,
                                                              line=line)
                num_session = 0
                sale._validate_create_session_from_sale_order(
                    event, num_session, line)
                if sale.project_by_task == 'yes':
                    if line.service_project_task:
                        project = line.service_project_task.project_id
                        project.event_id = line.event_id
                        project.analytic_account_id.event_id = line.event_id
            if not self.env.context.get('without_sale_name', False):
                sale.project_id.name = sale.name

    def _prepare_event_data(self, sale, line, name, project):
        tz = self.env.user.tz
        date_begin = _convert_to_utc_date(
            self.project_id.date_start, 0.0, tz=tz)
        date_end = _convert_to_utc_date(self.project_id.date, 0.0, tz=tz)
        if line and line.project_by_task == 'yes':
            date_begin = _convert_to_utc_date(
                line.start_date, line.start_hour, tz=tz)
            date_end = _convert_to_utc_date(
                line.end_date, line.end_hour, tz=tz)
        event_vals = {
            'name': name,
            'timezone_of_event': self.env.user.tz,
            'date_tz': self.env.user.tz,
            'project_id': project.id,
            'sale_order': sale.id,
            'date_begin': date_begin,
            'date_end': date_end,
        }
        return event_vals

    def _validate_create_session_from_sale_order(
            self, event, num_session, line):
        task_obj = self.env['project.task']
        tz = self.env.user.tz
        if line.project_by_task == 'yes':
            fec_ini = _convert_to_utc_date(
                line.start_date, line.start_hour, tz=tz)
            fec_limit = _convert_to_utc_date(
                line.end_date, line.end_hour, tz=tz)
        else:
            fec_ini = fields.Datetime.from_string(
                self.project_id.date_start)
            fec_limit = fields.Datetime.from_string(
                self.project_id.date)
        fec_ini = fec_ini.replace(day=1)
        if fec_ini.weekday() == 0:
            num_week = 0
        else:
            num_week = 1
        month = fec_ini.month
        while fec_ini.date() <= fec_limit.date():
            if month != fec_ini.month:
                month = fec_ini.month
                if fec_ini.weekday() == 0:
                    num_week = 0
                else:
                    num_week = 1
            if fec_ini.weekday() == 0:
                num_week += 1
            valid = False
            if line.project_by_task == 'yes':
                line_fec_ini = _convert_to_utc_date(
                    line.start_date, line.start_hour, tz=tz)
                if fec_ini.date() >= line_fec_ini.date():
                    valid = True
            else:
                if (fec_ini.date() >= fields.Datetime.from_string(
                        self.project_id.date_start).date()):
                    valid = True
            if valid:
                valid = task_obj._validate_event_session_month(line, fec_ini)
                if valid:
                    valid = task_obj._validate_event_session_week(
                        line, num_week)
                if valid:
                    valid = task_obj._validate_event_session_day(line, fec_ini)
                if valid:
                    num_session += 1
                    self._create_session_from_sale_line(
                        event, num_session, line, fec_ini)
            fec_ini = fec_ini + relativedelta(days=+1)

    def _create_session_from_sale_line(
            self, event, num_session, line, date):
        vals = self._prepare_session_data_from_sale_line(
            event, num_session, line, date)
        session = False
        if vals.get('duration', False) > 0:
            session = self.env['event.track'].create(vals)
            if line.service_project_task:
                session.tasks = [(4, line.service_project_task.id)]
                duration = sum(
                    line.service_project_task.sessions.mapped('duration'))
                line.service_project_task.planned_hours = duration
        return session

    def _prepare_session_data_from_sale_line(
            self, event, num_session, line, date):
        tz = self.env.user.tz
        new_date = False
        duration = False
        if self.project_id.working_hours:
            new_date, duration = (
                self.project_id.working_hours._calc_date_and_duration(date))
        if not duration:
            duration = line.product_uom_qty
            if line.performance:
                duration = ((line.performance * line.product_uom_qty)
                            if line.apply_performance_by_quantity else
                            line.performance)
        if not new_date:
            utc_dt = _convert_to_utc_date(
                date, line.start_hour if line.project_by_task == 'yes' else
                0.0, tz=tz)
        vals = {'name': (_('Session %s for %s') % (str(num_session),
                                                   line.product_id.name)),
                'event_id': event.id,
                'date': new_date or utc_dt,
                'duration': duration}
        return vals

    @api.multi
    def action_cancel(self):
        event_obj = self.env['event.event']
        res = super(SaleOrder, self).action_cancel()
        cond = [('sale_order', '=', self.id)]
        events = event_obj.search(cond)
        events.unlink()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    project_by_task = fields.Selection(
        selection=[('yes', 'Yes'), ('no', 'No')],
        related='order_id.project_by_task', string='Create project by task')
    start_date = fields.Date(string='Start date')
    start_hour = fields.Float(string='Start hour', default=0.0)
    end_date = fields.Date(string='End date')
    end_hour = fields.Float(string='End hour', default=0.0)
    apply_performance_by_quantity = fields.Boolean(
        string='performance = performance * quantity', default=True)

    @api.multi
    def product_id_change_with_wh(
        self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False,
        name='', partner_id=False, lang=False, update_tax=True,
        date_order=False, packaging=False, fiscal_position=False, flag=False,
            warehouse_id=False):
        product_obj = self.env['product.product']
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag,
            warehouse_id=warehouse_id)
        product = product_obj.browse(product)
        if product.recurring_service and (len(product.route_ids) == 0 or
           len(product.route_ids) > 1 or product.route_ids[0].id !=
           self.env.ref('procurement_service_project.route_serv_project').id):
            if res.get('warning') == {}:
                res['warning'].update({
                    'title': _('Error in recurring service product'),
                    'message': _('This product is a recurring service, But it'
                                 ' has NOT checked only the "Generate'
                                 ' procurement-task" option in their routes'
                                 ' defined, consequently, this product will'
                                 ' not create task in the event.')})
            else:
                res['warning']['title'] = (
                    res['warning'].get('title') + '. ' +
                    _('Error in recurring service product'))
                res['warning']['message'] = (
                    res['warning'].get('message') + '. ' +
                    _('This product is a recurring service, But it has NOT'
                      ' checked only the "Generate procurement-task" option in'
                      ' their routes defined, consequently, this product will'
                      ' not create task in the event.'))
        return res

    @api.onchange('start_hour', 'end_hour')
    def onchange_date_begin(self):
        self.ensure_one()
        if self.start_hour and self.end_hour:
            self.performance = self.end_hour - self.start_hour

    @api.multi
    def copy_data(self, default=None):
        self.ensure_one()
        if not default:
            default = {}
        if self.product_id and self.product_id.recurring_service:
            default.update({'event_id': False})
        res = super(SaleOrderLine, self).copy_data(default=default)
        return res[0] if res else {}
