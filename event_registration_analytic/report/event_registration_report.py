# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, tools


class EventRegistrationReport(models.Model):
    _name = 'event.registration.report'
    _description = 'Report with counters for event registrations'
    _auto = False
    _order = ('address_id, event_id, date')

    address_id = fields.Many2one(
        comodel_name='res.partner', string='Center', readonly=True)
    event_id = fields.Many2one(
        comodel_name='event.event', string='Event', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    high_counter = fields.Integer(string='Highs', readonly=True)
    down_counter = fields.Integer(string='Downs', readonly=True)
    number_records_total = fields.Integer(
        string='Number records total', readonly=True)
    unsubscribe_requests_counter = fields.Integer(
        string='Unsubscribe requests', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'event_registration_report')
        cr.execute("""
        CREATE OR REPLACE VIEW event_registration_report AS (
       select cast(cast(t.event_id as varchar) || t.date as integer) as id,
       t.address_id, t.event_id, to_date(to_char(to_date(t.date,'YYYYMM'),
       'YYYY-MM-') || extract (day from
       (select date_trunc('month',to_date(t.date,'YYYYMM')) +
       '1month' ::interval -'1sec' ::interval)),'YYYY-MM-DD') as date,
       sum(t.high_counter) as high_counter, sum(t.down_counter) as
       down_counter, sum(t.unsubscribe_requests_counter) as
       unsubscribe_requests_counter, sum(t.high_counter) - sum(t.down_counter)
       + (select count(x.date_start) from event_registration x where
       x.event_id = t.event_id and x.state != 'draft' and
       to_char(x.date_start,'YYYYMM') < t.date) -
       (select count(u.date_end) from event_registration u where u.event_id =
       t.event_id and u.state != 'draft' and
       to_char(u.date_end,'YYYYMM') < t.date) as number_records_total
       from
       ((select ev.address_id as address_id, ev.id as event_id,
       to_char(re.date_start,'YYYYMM') as date, count(re.date_start) as
       high_counter, 0 as down_counter, 0 as unsubscribe_requests_counter
       from   event_event ev,
             event_registration re
       where  re.state != 'draft'
         and  re.date_start is not null
         and  ev.id     = re.event_id
       group by ev.address_id, ev.id, to_char(re.date_start,'YYYYMM')
       order by ev.address_id, ev.id, to_char(re.date_start,'YYYYMM'))
       UNION ALL
       (select ev.address_id as address_id, ev.id as event_id,
       to_char(re.date_end,'YYYYMM') as date, 0 as high_counter,
       count(re.date_end) as down_counter, 0 as unsubscribe_requests_counter
       from event_event ev,
            event_registration re
       where  re.state != 'draft'
         and  re.date_end is not null
         and  ev.id     = re.event_id
       group by ev.address_id, ev.id, to_char(re.date_end,'YYYYMM')
       order by ev.address_id, ev.id, to_char(re.date_end,'YYYYMM'))
       UNION ALL
       (select ev.address_id as address_id, ev.id as event_id,
              to_char(re.removal_date,'YYYYMM') as date, 0 as high_counter,
              0 as down_counter, count(re.removal_date) as
              unsubscribe_requests_counter
       from   event_event ev,
              event_registration re
       where  re.state != 'draft'
         and  re.removal_date is not null
         and  ev.id     = re.event_id
       group by ev.address_id, ev.id, to_char(re.removal_date,'YYYYMM')
       order by ev.address_id, ev.id, to_char(re.removal_date,'YYYYMM'))) as t
       group by t.address_id, t.event_id, t.date
       order by t.address_id, t.event_id, t.date)""")
