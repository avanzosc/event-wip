# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Event Worker Portal",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "category": "Event Management",
    "depends": [
        "partner_student_course",
        "event_track_assistant",
        "event_track_info",
        "hr_contract",
        "hr_skill",
        "hr_experience",
        "calendar_holiday",
        "note",
        "portal"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/event_view.xml",
        "views/hr_employee_view.xml",
    ],
    "installable": True,
    "post_init_hook": "create_user_restricted_group",
}
