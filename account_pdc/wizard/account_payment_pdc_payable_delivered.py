from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentPdcPayableDelivered(models.TransientModel):
    _name = 'account.payment.pdc.payable.delivered'
    _description = 'Account Payment PDC Payable Delivered Wizard'

    delivered_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )

    def action_delivered_pdc_payable(self):
        """ delivered pdc payable """
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        payment = self.env[active_model].browse(active_ids)
        payment.action_delivered_pdc_payable(
                delivered_date=self.delivered_date,
            )

    def action_received_pdc_payable(self):
        """ delivered pdc payable """
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        payment = self.env[active_model].browse(active_ids)
        payment.action_received_pdc_payable(
                received_date=self.delivered_date,
            )
