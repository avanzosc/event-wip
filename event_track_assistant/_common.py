# -*- coding: utf-8 -*-
# Copyright © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import date as datetype
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
from openerp import fields

str2datetime = fields.Datetime.from_string
date2str = fields.Date.to_string


def _convert_to_local_date(date, tz=u'UTC'):
    if not date:
        return False
    if not tz:
        tz = u'UTC'
    new_date = str2datetime(date) if isinstance(date, str) else date
    new_date = new_date.replace(tzinfo=utc)
    local_date = new_date.astimezone(timezone(tz)).replace(tzinfo=None)
    return local_date


def _convert_to_utc_date(date, time=0.0, tz=u'UTC'):
    if not date:
        return False
    if not tz:
        tz = u'UTC'
    date = date2str(date) if isinstance(date, datetype) else date
    date = str2datetime(date) if isinstance(date, str) else date
    date += relativedelta(hours=float(time))
    local = timezone(tz)
    local_date = local.localize(date, is_dst=None)
    utc_date = local_date.astimezone(utc).replace(tzinfo=None)
    return utc_date


def _convert_time_to_float(date, tz=u'UTC'):
    if not date:
        return False
    if not tz:
        tz = u'UTC'
    local_time = _convert_to_local_date(date, tz=tz)
    hour = float(local_time.hour)
    minutes = float(local_time.minute) / 60
    seconds = float(local_time.second) / 360
    return (hour + minutes + seconds)
