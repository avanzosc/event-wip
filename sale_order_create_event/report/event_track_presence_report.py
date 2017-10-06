# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, tools


class EventTrackPresenceReport(models.Model):
    _name = "event.track.presence.report"
    _description = "Event track presence report"
    _auto = False

    employee_id = fields.Many2one(
        comodel_name='res.partner', string='Employee', readonly=True)
    customer_id = fields.Many2one(
        comodel_name='res.partner', string='Customer', readonly=True)
    city = fields.Char(string='City', readonly=True)
    street = fields.Char(string='Street', readonly=True)
    event_id = fields.Many2one(
        comodel_name='event.event', string='Event', readonly=True)
    start_hour = fields.Char(string='Start hour', readonly=True)
    end_hour = fields.Char(string='End hour', readonly=True)
    session_duration = fields.Float(string='Session duration', readonly=True)
    days = fields.Char(string='Days', readonly=True)
    session_name = fields.Char(string='Job', readonly=True)

    def _select(self):
        select_str = """
        select p.partner as employee_id, s.partner_id as customer_id,
               COALESCE(r.street2,r.street) as street, r.city as city,
               p.event as event_id, p.start_hour as start_hour,
               p.end_hour as end_hour,
               (p.session_duration * (select count(distinct(p2.session_day))
                                      from   event_track_presence p2
                                      where  p2.event = p.event
                                        and  p2.partner = p.partner
                                        and  p2.start_hour = p.start_hour
                                        and  p2.end_hour = p.end_hour))
                as session_duration,
                array_to_string(array_agg(distinct(replace(replace(replace(
                replace(replace(replace(replace(p.session_day,'0','L'),'1','M')
                ,'2','X'),'3','J'),'4','V'),'5','S'),'6','D'))),',') as days,
               (select t.name
                from   event_track t
                where  t.event_id = p.event
                  and  t.id = (select min(t2.id)
                                from  event_track t2
                                where t2.event_id = p.event)) as session_name,
               min(p.id) as id
        """
        return select_str

    def _from(self):
        from_str = """
        from   event_track_presence p
               inner join event_track t on t.id = p.session
               inner join event_event e on e.id = p.event
               inner join sale_order s on s.id = e.sale_order
               inner join res_partner r on r.id = s.partner_id
        """
        return from_str

    def _where(self):
        where_str = """
        where  p.state != 'canceled'
        """
        return where_str

    def _group_by(self):
        group_by_str = """
        group  by 1, 2, 3, 4, 5, 6, 7, 8
        """
        return group_by_str

    def _order_by(self):
        order_by_str = """
        order  by 1, 2, 5, 9
        """
        return order_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (%s %s %s %s %s)
        """ % (self._table, self._select(), self._from(), self._where(),
               self._group_by(), self._order_by()))
