# -*- coding: utf-8 -*-
# @authors: Alexander Ezquevo <alexander@acysos.com>
# Copyright (C) 2016  Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError
from datetime import timedelta


class EventTrackLocation(models.Model):
    _inherit = 'event.track.location'

    def _get_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(string='Company', comodel_name='res.company',
                                 default=_get_company)
    capacity = fields.Integer(string='Capacity', required=True)
    reservation_days = fields.One2many(
        string='Reservation days',
        comodel_name='event.track.location.reservation',
        inverse_name='et_location_id')

    @api.multi
    def do_reservation(self, day, duration, track_id=False):
        reservation_obj = self.env['event.track.location.reservation']
        for location in self:
            if location.check_availability(day, duration):
                reservation_obj.create({
                    'et_location_id': location.id,
                    'day': day,
                    'duration': duration,
                    'track_id': track_id,
                })
            else:
                raise UserError(
                    _('Location %s is reserved for date %s') %
                    (location.name, day))

    @api.multi
    def do_unreservation(self, track):
        self.mapped('reservation_days').filtered(
            lambda r: r.track_id == track).unlink()

    @api.multi
    def check_availability(self, day, duration):
        self.ensure_one()
        end_day = fields.Datetime.to_string(fields.Datetime.from_string(day) +
                                            timedelta(hours=duration))
        reservations = self.reservation_days.filtered(
            lambda r: (r.day < end_day and r.end_date >= end_day) or
                      (r.day <= day and r.end_date > day) or
                      (r.day > day and r.end_date < end_day))
        available = True if len(reservations) == 0 else False
        return available


class EventTrackLocationReservation(models.Model):
    _name = 'event.track.location.reservation'

    @api.depends('day', 'duration')
    def _compute_end_date(self):
        for res in self.filtered('day'):
            res.end_date = fields.Datetime.from_string(res.day) +\
                timedelta(hours=res.duration)

    et_location_id = fields.Many2one(
        string='Location', comodel_name='event.track.location',
        required=True)
    day = fields.Datetime(string='Start Date', required=True)
    duration = fields.Float(string='Duration')
    end_date = fields.Datetime(
        string='End Date', compute='_compute_end_date', store=True)
    track_id = fields.Many2one(string='Session', comodel_name='event.track')

    @api.constrains('et_location_id', 'day', 'duration')
    def _check_location_availability(self):
        for record in self:
            if not len(record.et_location_id.reservation_days.filtered(
                lambda r: r.id != record.id and
                ((r.day < record.end_date and r.end_date >= record.end_date) or
                 (r.day <= record.day and r.end_date > record.day) or
                 (r.day > record.day and r.end_date < record.end_date)))) == 0:
                raise ValidationError(
                    _('Location %s is reserved for date %s') %
                    (record.et_location_id.name, record.day))


class EventTrack(models.Model):
    _inherit = 'event.track'

    @api.model
    def create(self, vals):
        track = super(EventTrack, self).create(vals)
        if track.location_id:
            track.location_id.do_reservation(
                track.date, track.duration, track.id)
        return track

    @api.multi
    def write(self, vals):
        for track in self:
            location_change = 'location_id' in vals and\
                              (vals.get('location_id') != track.location_id.id)
            if location_change:
                track.location_id.do_unreservation(track)
            super(EventTrack, track).write(vals)
            if location_change:
                track.location_id.do_reservation(
                    track.date, track.duration, track.id)
        return True
