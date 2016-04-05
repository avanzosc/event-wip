# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _


class HrTypeHour(models.Model):
    _name = 'hr.type.hour'
    _description = 'Type hours'

    name = fields.Char('Description', translate=True)

    @api.multi
    def write(self, vals):
        type_hours = self.env['hr.type.hour']
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_working')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_sunday')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive_work')
        for type in self:
            if type.id in type_hours.ids:
                raise exceptions.Warning(
                    _('You can not change a type of time created by the'
                      ' system'))
        return super(HrTypeHour, self).write(vals)

    @api.multi
    def unlink(self):
        type_hours = self.env['hr.type.hour']
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_working')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_sunday')
        type_hours += self.env.ref(
            'sale_order_create_event_hour.type_hour_festive_work')
        for type in self:
            if type.id in type_hours.ids:
                raise exceptions.Warning(
                    _('You can not delete a type of time created by the'
                      ' system'))
        return super(HrTypeHour, self).unlink()
