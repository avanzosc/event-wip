# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, tools


class EventRegistrationReport(models.Model):
    _inherit = 'event.registration.report'

    num_center_invoices = fields.Integer(
        string='# Invoices center', readonly=True)
    num_student_invoices = fields.Integer(
        string='# Invoices student', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'event_registration_report')
        cr.execute("""
        CREATE OR REPLACE VIEW event_registration_report AS (
       select cast(cast(ev.id as varchar) ||
              to_char(evday.edate,'YYMM') as integer) as id,
              ev.address_id as address_id, ev.id as event_id,
              to_date(to_char(evday.edate,'YYYY-MM-') || extract (day from (
                     select date_trunc('month',
                     to_date(to_char(evday.edate,'YYYYMM'), 'YYYYMM')) +
                     '1month' ::interval -'1sec' ::interval)),
                     'YYYY-MM-DD') as date,
              (select count(*)
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(date_start,'YYYY-MM') =
                     to_char(evday.edate,'YYYY-MM')) as high_counter,
              (select count(*)
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(date_end,'YYYY-MM') =
                     to_char(evday.edate,'YYYY-MM')) as down_counter,
              (select count(*)
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(date_start,'YYYY-MM') <=
                     to_char(evday.edate,'YYYY-MM'))
                     -
              (select count(*)
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(date_end,'YYYY-MM') <=
                     to_char(evday.edate,'YYYY-MM')) as number_records_total,
              (select count(*)
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(removal_date,'YYYY-MM') = to_char(evday.edate,
                     'YYYY-MM')) as unsubscribe_requests_counter,
              (select case when sum(l.quantity) is not null
                      then sum(l.quantity) else 0 end
               from   account_invoice_line l,
                      account_invoice i,
                      event_event ev2,
                      sale_order s
               where  ev2.id = ev.id
                 and  ev2.sale_order = s.id
                 and  s.payer = 'school'
                 and  i.sale_order_id = s.id
                 and  i.state <> 'cancel'
                 and  to_char(i.date_invoice,'YYYY-MM') =
                 to_char(evday.edate,'YYYY-MM')
                 and  l.invoice_id = i.id) as num_center_invoices,
              (select case when count(i.*) is not null
                      then count(i.*) else 0 end
               from   account_invoice i,
                      event_event ev2,
                      sale_order s
               where  ev2.id = ev.id
                 and  ev2.sale_order = s.id
                 and  s.payer = 'student'
                 and  i.sale_order_id = s.id
                 and  i.state <> 'cancel'
                 and  to_char(i.date_invoice,'YYYY-MM') =
                 to_char(evday.edate,'YYYY-MM')) as num_student_invoices
        from event_event ev left join
        (select generate_series(e.date_begin::date,e.date_end::date,
        '1 month'::interval), e.id from event_event e) as evday(edate, e)
        on e=ev.id
       group by 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
       order by 2, 3, 4)""")
