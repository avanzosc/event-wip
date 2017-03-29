# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def assign_sequence_to_event_track(cr):
    cr.execute("""update event_track
                  set num_session = rtrim(substr(name,8,2))::int;""")


def migrate(cr, version):
    if not version:
        return
    assign_sequence_to_event_track(cr)
