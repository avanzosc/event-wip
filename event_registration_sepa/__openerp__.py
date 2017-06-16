# -*- coding: utf-8 -*-
# (c) 2016 Esther Martín - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Event Registration Sepa",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Esther Martín <esthermartin@avanzosc.es>",
    ],
    "category": "Event Management",
    "depends": [
        "partner_event",
        "account_banking_sepa_direct_debit",
        "hr_employee_catch_partner",
        "event_registration_analytic",
    ],
    'data': ['views/payment_mode_view.xml',
             ],
    "installable": True,
}
