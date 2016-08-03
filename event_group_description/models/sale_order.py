# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        for sale in self:
            for line in sale.order_line:
                if not line.group_description:
                    line.button_group_description()
        res = super(SaleOrder, self).action_button_confirm()
        for sale in self:
            for line in sale.order_line:
                if line.service_project_task:
                    pos = line.group_description.find('-')
                    line.service_project_task.write(
                        {'name': line.group_description[pos+1:],
                         'description': line.group_description[pos+1:]})
                    project = line.service_project_task.project_id
                    if project and project.analytic_account_id:
                        project.analytic_account_id.write(
                            {'name': line.group_description[pos+1:]})
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
        event_obj = self.env['event.event']
        for line in self:
            description = line.order_id.name + '-' + str(line.sequence)
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
            utc_dt = event_obj._put_utc_format_date(line.start_date,
                                                    line.start_hour)
            local = event_obj._convert_date_to_local_format_with_hour(
                str(utc_dt)[0:19])
            description += '-' + str(local)[11:16]
            utc_dt = event_obj._put_utc_format_date(line.end_date,
                                                    line.end_hour)
            local = event_obj._convert_date_to_local_format_with_hour(
                str(utc_dt)[0:19])
            description += '-' + str(local)[11:16]
            line.group_description = description
