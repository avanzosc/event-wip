# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _
from openerp.addons.event_track_assistant._common import\
    _convert_to_utc_date, _convert_to_local_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for line in self.mapped('order_line').filtered(
                lambda l: l.product_id.recurring_service and
                not l.group_description):
            line.button_group_description()
        res = super(SaleOrder, self).action_button_confirm()
        for line in self.mapped('order_line').filtered(
                lambda l: l.product_id.recurring_service and
                l.service_project_task):
            pos = line.group_description.find('-')
            name = u"\n{}: {}".format(line.order_id.name,
                                      line.group_description[pos+1:])
            line.service_project_task.write(
                {'name': name,
                 'description': line.group_description[pos+1:]})
            project = line.service_project_task.project_id
            if project and project.analytic_account_id:
                project.analytic_account_id.write(
                    {'name': name})
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    group_description = fields.Char(
        string='Group description', copy=False)
    courses = fields.Char(
        string='Courses', copy=False)
    days = fields.Char(
        string='Days', compute='_compute_line_days', store=True, copy=False)

    @api.depends('monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                 'saturday', 'sunday')
    @api.multi
    def _compute_line_days(self):
        for line in self:
            line.days = ''
            if line.monday:
                line.days = (_('Monday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Monday')))
            if line.tuesday:
                line.days = (_('Tuesday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Tuesday')))
            if line.wednesday:
                line.days = (_('Wednesday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Wednesday')))
            if line.thursday:
                line.days = (_('Thursday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Thursday')))
            if line.friday:
                line.days = (_('Friday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Friday')))
            if line.saturday:
                line.days = (_('Saturday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Saturday')))
            if line.sunday:
                line.days = (_('Sunday') if len(line.days) == 0 else
                             u"{}-{}".format(line.days, _('Sunday')))

    @api.multi
    def button_group_description(self):
        tz = self.env.user.tz
        for line in self:
            description = u'{}-{}'.format(line.order_id.name, line.sequence)
            if line.courses:
                description += '-' + line.courses
            if line.monday:
                description += '-' + _('Monday')
            if line.tuesday:
                description += '-' + _('Tuesday')
            if line.wednesday:
                description += '-' + _('Wednesday')
            if line.thursday:
                description += '-' + _('Thursday')
            if line.friday:
                description += '-' + _('Friday')
            if line.saturday:
                description += '-' + _('Saturday')
            if line.sunday:
                description += '-' + _('Sunday')
            if line.product_id.recurring_service:
                utc_dt = _convert_to_utc_date(
                    line.start_date, line.start_hour, tz)
                local = _convert_to_local_date(utc_dt, tz)
                description += '-' + str(local)[11:16]
                utc_dt = _convert_to_utc_date(
                    line.end_date, line.end_hour, tz)
                local = _convert_to_local_date(utc_dt, tz)
                description += '-' + str(local)[11:16]
            line.group_description = description
