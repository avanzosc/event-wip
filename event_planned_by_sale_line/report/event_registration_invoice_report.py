# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, tools


class EventRegistrationInvoiceReport(models.Model):
    _name = 'event.registration.invoice.report'
    _description = 'Report with counters and invoices for event registrations'
    _auto = False
    _order = ('address_id, event_id, date')

    address_id = fields.Many2one(
        comodel_name='res.partner', string='Center', readonly=True)
    event_id = fields.Many2one(
        comodel_name='event.event', string='Event', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    student_counter = fields.Integer(string='Students', readonly=True)
    num_center_invoices = fields.Integer(
        string='# Invoices center', readonly=True)
    num_student_invoices = fields.Integer(
        string='# Invoices student', readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'event_registration_invoice_report')
        cr.execute("""
        CREATE OR REPLACE VIEW event_registration_invoice_report AS (
       select cast(cast(ev.id as varchar) ||
              to_char(evday.edate,'YYMM') as integer) as id,
              ev.address_id as address_id, ev.id as event_id,
              to_date(to_char(evday.edate,'YYYY-MM-') || extract (day from (
                     select date_trunc('month',
                     to_date(to_char(evday.edate,'YYYYMM'), 'YYYYMM')) +
                     '1month' ::interval -'1sec' ::interval)),
                     'YYYY-MM-DD') as date,
              (select CASE when exists (select *
               from event_registration
               where event_id = ev.id and
                     state != 'draft' and
                     employee is null and
                     to_char(date_start,'YYYY-MM') =
                     to_char(evday.edate,'YYYY-MM')) then (select count(*)
              from event_registration
              where event_id = ev.id and
                    state != 'draft' and
                    employee is null and
                    to_char(date_start,'YYYY-MM') =
                    to_char(evday.edate,'YYYY-MM'))
               else
              (select count(*)
              from event_registration
              where event_id = ev.id and
                    state != 'draft' and
                    employee is null and
                    to_char(date_end,'YYYY-MM') =
                    to_char(evday.edate,'YYYY-MM')) end) as student_counter,
               (select case when sum(l2.quantity) is not null
                      then sum(l2.quantity) else 0 end
                from  event_event ev2
                inner join account_invoice_line l2 on
                l2.invoice_sale_order_id = ev2.sale_order
               where  ev2.id = ev.id
                 and  l2.invoice_payer = 'school'
                 and  l2.invoice_state <> 'cancel'
                 and  to_char(l2.invoice_date_invoice,'YYYY-MM') =
                 to_char(evday.edate,'YYYY-MM')) as num_center_invoices,
              (select case when count(i3.*) is not null
                      then count(i3.*) else 0 end
               from   event_event ev3
               inner join account_invoice i3 on
               i3.sale_order_id = ev3.sale_order
               where  ev3.id = ev.id
                 and  i3.sale_order_payer = 'student'
                 and  i3.state <> 'cancel'
                 and  to_char(i3.date_invoice,'YYYY-MM') =
                 to_char(evday.edate,'YYYY-MM')) as num_student_invoices
        from event_event ev left join
        (select generate_series(e.date_begin::date,e.date_end::date,
        '1 month'::interval), e.id from event_event e) as evday(edate, e)
        on e=ev.id
       group by 1, 2, 3, 4, 5, 6, 7
       order by 2, 3, 4)""")
