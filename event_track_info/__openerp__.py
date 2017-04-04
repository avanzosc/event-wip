# -*- coding: utf-8 -*-
# (c) 2016 Ainara Galdona - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Event Track Info",
    "version": "8.0.1.3.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Ainara Galdona <ainaragaldona@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es",
    ],
    "category": "Event Management",
    "depends": [
        "product_training_plan",
        "event_report",
        "sale_order_create_event"
    ],
    "data": [
        "wizard/product_training_plan_wizard.xml",
        "views/event_track_view.xml",
        "views/event_event_view.xml",
    ],
    "installable": True,
}
