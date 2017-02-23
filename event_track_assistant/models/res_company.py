# -*- coding: utf-8 -*-
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, exceptions, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    daytime_start_hour = fields.Float(
        string='Daytime Start Hour', default=6.0,
        help='Start hour for daytime, it does not have into account'
        ' user timezone.')
    nighttime_start_hour = fields.Float(
        string='Nighttime Start Hour', default=22.0,
        help='Start hour for nighttime, it does not have into account'
        ' user timezone.')

    @api.constrains('daytime_start_hour', 'nighttime_start_hour')
    def _check_start_hours(self):
        for record in self:
            if record.daytime_start_hour < 0.0 or\
                    record.daytime_start_hour > 24.0 or\
                    record.nighttime_start_hour < 0.0 or\
                    record.nighttime_start_hour > 24.0:
                raise exceptions.ValidationError(
                    _('Start hours must be between 0 and 24.'))
            if record.daytime_start_hour >= record.nighttime_start_hour:
                raise exceptions.ValidationError(
                    _('Nighttime start hour must be greater than daytime start'
                      ' hour.'))
