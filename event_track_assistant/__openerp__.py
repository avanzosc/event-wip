# -*- coding: utf-8 -*-
# Copyright © 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Event Track Assistant",
    "version": "8.0.1.3.0",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
    ],
    "category": "Event Management",
    "depends": [
        "website_event_track",
        "partner_event",
        "crm_claim",
        "event_registration_mass_mailing",
        "warning"
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/event_track_assistant.xml",
        "data/event_track_assistant_data.xml",
        "wizard/wiz_event_append_assistant_view.xml",
        "wizard/wiz_event_delete_assistant_view.xml",
        "wizard/wiz_event_confirm_assistant_view.xml",
        "wizard/wiz_change_session_hour_view.xml",
        "wizard/wiz_impute_in_presence_from_session_view.xml",
        "wizard/wiz_registration_to_another_event_view.xml",
        "wizard/wiz_complete_presence_view.xml",
        "wizard/wiz_send_email_to_registrations_view.xml",
        "wizard/wiz_change_session_duration_view.xml",
        "wizard/wiz_event_registration_confirm_view.xml",
        "views/event_event_view.xml",
        "views/event_registration_view.xml",
        "views/event_track_view.xml",
        "views/event_track_presence_view.xml",
        "views/res_partner_view.xml",
        "views/crm_claim_view.xml",
        "views/res_company_view.xml",
        "views/marketing_config_settings_view.xml",
    ],
    "installable": True,
}
