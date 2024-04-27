from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # is_pdc_receivable_entry = fields.Boolean(related='move_id.is_pdc_receivable_entry', store=True)

    def action_post(self):
        """ inherit to set receivable payment """
        super().action_post()
        for payment in self:
            if payment.is_pdc_payment and payment.move_id:
                payment.move_id.is_pdc_receivable_entry = True
                if payment.move_id.line_ids:
                    for line in payment.move_id.line_ids:
                        if line.account_id.user_type_id.type == 'receivable':
                            line.is_pdc_receivable_entry = True

