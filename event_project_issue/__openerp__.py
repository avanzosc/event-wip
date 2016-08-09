# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Event Project Issue",
    'version': '8.0.1.1.0',
    'license': "AGPL-3",
    'author': "AvanzOSC",
    'website': "http://www.avanzosc.es",
    'contributors': [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "category": "Event Management",
    "depends": [
        'project_issue',
        'website_event_track',
        'event_track_assistant',
        'sale_order_create_event'
    ],
    "data": [
        'views/event_event_view.xml',
        'views/event_track_view.xml',
        'views/project_issue_view.xml',
    ],
    "installable": True,
}
