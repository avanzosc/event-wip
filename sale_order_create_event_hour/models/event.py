# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    type_hour = fields.Many2one(
        comodel_name='hr.type.hour', string='Type hour')


class EventTrack(models.Model):
    _inherit = 'event.track'

    type_hour = fields.Many2one(
        comodel_name='hr.type.hour', string='Type hour')

    @api.model
    def create(self, vals):
        session_date = self.env['event.event'].\
            _convert_date_to_local_format_with_hour(
                fields.Datetime.to_string(vals.get('date')))
        if session_date.weekday() == 6:
            vals['type_hour'] = self.env.ref(
                'sale_order_create_event_hour.type_hour_sunday').id
        return super(EventTrack, self).create(vals)


class EventTrackPresence(models.Model):
    _inherit = 'event.track.presence'

    type_hour = fields.Many2one(
        comodel_name='hr.type.hour', string='Type hour')


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        wiz_vals = self._update_wizard_vals(wiz_vals)
        wiz_vals.update({'type_hour': self.event_id.type_hour.id})
        return wiz_vals

    def _prepare_wizard_reg_cancel_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_reg_cancel_vals()
        wiz_vals = self._update_wizard_vals(wiz_vals)
        return wiz_vals

    def _update_wizard_vals(self, wiz_vals):
        event_obj = self.env['event.event']
        date_start = self.date_start if self.date_start else\
            self.event_id.date_begin
        date_end = self.date_end if self.date_end else self.event_id.date_end
        from_date = event_obj._convert_date_to_local_format_with_hour(
            date_start)
        start_time = event_obj._convert_times_to_float(date_start)
        to_date = event_obj._convert_date_to_local_format_with_hour(date_end)
        end_time = event_obj._convert_times_to_float(date_end)
        wiz_vals.update({
            'from_date': from_date.date(),
            'min_from_date': date_start,
            'start_time': start_time,
            'to_date': to_date.date(),
            'max_to_date': date_end,
            'end_time': end_time,
        })
        return wiz_vals
