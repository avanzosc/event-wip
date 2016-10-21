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

    @api.multi
    def registration_open(self):
        self.ensure_one()
        wiz_obj = self.env['wiz.event.append.assistant']
        result = super(EventRegistration, self).registration_open()
        wiz = wiz_obj.browse(result['res_id'])
        wiz.update({'type_hour': self.event_id.type_hour})
        return result

    def _prepare_wizard_registration_open_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_registration_open_vals()
        wiz_vals = self._update_wizard_vals(wiz_vals)
        return wiz_vals

    def _prepare_wizard_reg_cancel_vals(self):
        wiz_vals = super(EventRegistration,
                         self)._prepare_wizard_reg_cancel_vals()
        wiz_vals = self._update_wizard_vals(wiz_vals)
        return wiz_vals

    def _update_wizard_vals(self, wiz_vals):
        event_obj = self.env['event.event']
        if self.date_start:
            start_time = event_obj._convert_times_to_float(self.date_start)
            wiz_vals.update({'from_date':
                             event_obj._convert_date_to_local_format_with_hour(
                                 self.date_start).date(),
                             'min_from_date': self.date_start,
                             'start_time': start_time})
        else:
            start_time = event_obj._convert_times_to_float(
                self.event_id.date_begin)
            wiz_vals.update({'from_date':
                             event_obj._convert_date_to_local_format_with_hour(
                                 self.event_id.date_begin).date(),
                             'min_from_date': self.event_id.date_begin,
                             'start_time': start_time})
        if self.date_end:
            end_time = event_obj._convert_times_to_float(self.date_end)
            wiz_vals.update({'to_date':
                             event_obj._convert_date_to_local_format_with_hour(
                                 self.date_end).date(),
                             'max_to_date': self.date_end,
                             'end_time': end_time})
        else:
            end_time = event_obj._convert_times_to_float(
                self.event_id.date_end)
            wiz_vals.update({'to_date':
                             event_obj._convert_date_to_local_format_with_hour(
                                 self.event_id.date_end).date(),
                             'max_to_date': self.event_id.date_end,
                             'end_time': end_time})
        wiz_vals.update({'start_time': start_time,
                         'end_time': end_time})
        return wiz_vals
