from odoo import _, fields, models


class AccountHandOverReject(models.TransientModel):
    _name = 'account.hand.over.reject'
    _description = 'Account Hand Over Reject Wizard'

    reason = fields.Char()

    def action_reject(self):
        """ reject hand over """
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        record = self.env[active_model].browse(active_ids)
        reject_reason = self.reason or ''
        record.action_reject(reason=reject_reason)
