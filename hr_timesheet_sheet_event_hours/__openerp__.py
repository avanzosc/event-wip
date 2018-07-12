# -*- coding: utf-8 -*-
# Copyright © 2018 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Hr Timesheet Sheet Event Hours",
    "version": "8.0.2.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "category": "Event Management",
    "depends": [
        "event_substitution",
        "hr_timesheet_sheet",
        "hr_contract_history"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_timesheet_sheet_sheet_view.xml",
    ],
    "installable": True,
    "auto-install": True,
}
