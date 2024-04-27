from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # there is no easiy way to unlink all views at once as system restrict it
    view = env.ref('account_pdc.account_journal_form_inherit', False)
    if view:
        if view.inherit_children_ids:
            view.inherit_children_ids.unlink()
        view.unlink()
