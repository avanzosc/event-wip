# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _
from openerp.tools import config


class HrTypeHour(models.Model):
    _name = 'hr.type.hour'
    _description = 'Type hours'
    _rec_name = 'name'

    name = fields.Char(string='Description', translate=True, required=True)

    def _get_non_editable_type_hours(self):
        type_hours = self.env['hr.type.hour']
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_working')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_sunday')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive_work')
        return type_hours

    @api.multi
    def write(self, vals):
        if (config['test_enable'] and
                not self.env.context.get('check_write_type_hour')):
            return super(HrTypeHour, self).write(vals)
        type_hours = self._get_non_editable_type_hours()
        if any(self.filtered(lambda t: t.id in type_hours.ids)):
            raise exceptions.Warning(
                _('You can not change a type of time created by the system'))
        return super(HrTypeHour, self).write(vals)

    @api.multi
    def unlink(self):
        type_hours = self._get_non_editable_type_hours()
        if any(self.filtered(lambda t: t.id in type_hours.ids)):
            raise exceptions.Warning(
                _('You can not delete a type of time created by the system'))
        return super(HrTypeHour, self).unlink()
