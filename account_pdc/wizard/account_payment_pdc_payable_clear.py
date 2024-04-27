from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentPdcPayableClear(models.TransientModel):
    _name = 'account.payment.pdc.payable.clear'
    _description = 'Account Payment PDC Payable Clear Wizard'

    clear_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )

    def action_clear_pdc_payable(self):
        """ clear pdc payable """
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        payment = self.env[active_model].browse(active_ids)
        payment.action_clear_pdc_payable(
                clear_date=self.clear_date,
            )
