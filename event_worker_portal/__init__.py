# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import SUPERUSER_ID, _


def create_user_restricted_group(cr, registry):
    group_obj = registry['res.groups']
    model_access_obj = registry['ir.model.access']
    group_id = registry['ir.model.data'].get_object_reference(
        cr, SUPERUSER_ID, 'event', 'group_event_user')[1]
    new_group_id = group_obj.copy(cr, SUPERUSER_ID, group_id, default={})
    group_obj.write(cr, SUPERUSER_ID, new_group_id, {
        'name': _('Event restricted worker'),
        'implied_ids': [(6, 0, [])]})
    group_obj.write(cr, SUPERUSER_ID, group_id, {
        'implied_ids': [(4, new_group_id)]})
    cond = [('model', 'in',
             ('event.event', 'event.registration', 'event.track'))]
    model_ids = registry['ir.model'].search(cr, SUPERUSER_ID, cond)
    cond = [('group_id', '=', new_group_id),
            ('model_id', 'in', model_ids)]
    model_access_ids = model_access_obj.search(cr, SUPERUSER_ID, cond)
    vals = {'perm_read': True,
            'perm_create': False,
            'perm_write': False,
            'perm_unlink': False}
    model_access_obj.write(cr, SUPERUSER_ID, model_access_ids, vals)
