from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # there is no easiy way to unlink all views at once as system restrict it
    view = env.ref('account_pdc.account_payment_pdc_receivable_form_inherit_primary', False)
    if view:
        if view.inherit_children_ids:
            view.inherit_children_ids.unlink()
        view.unlink()
    view = env.ref('account_pdc.account_payment_form_inherit', False)
    if view:
        if view.inherit_children_ids:
            view.inherit_children_ids.unlink()
        view.unlink()
    view = env.ref('account_pdc.account_payment_register_form_inherit', False)
    if view:
        view.unlink()
    view = env.ref('account_pdc.account_payment_pdc_payable_search_primary', False)
    if view:
        view.unlink()
