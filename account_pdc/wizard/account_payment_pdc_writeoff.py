from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountPaymentPdcWriteoff(models.TransientModel):
    _name = 'account.payment.pdc.writeoff'
    _description = 'Account Payment PDC Write Off Wizard'

    date = fields.Date(
        string='Transaction Date',
        default=fields.Date.context_today,
    )
    ref = fields.Char(
        string='Reference',
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        required=True,
    )

    def action_register_write_off(self):
        """ register write off for bank """
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model != 'account.payment':
            raise ValidationError(_('Please open Cheque'))

        payment = self.env[active_model].browse(active_id)
        if payment.is_pdc_payment:
            move = payment._create_pdc_journal_entry(
                journal=payment.journal_id,
                partner=payment.partner_id,
                label='Cheque Write off %s - %s' % (payment.ref, payment.name),
                amount=abs(payment._get_payment_amount()),
                debit_account=self.account_id,
                credit_account=payment.destination_account_id,
                amount_currency=abs(payment._get_payment_amount(company_currency=False)),
                currency=payment.currency_id,
                ref=self.ref,
                date=self.date,
                cheque_payment_type='writeoff'
            )
            payment.write_off_payment_id = move.id
            payment.pdc_state = 'writeoff'
            if hasattr(payment, 'invoice_matching_ids'):
                writeoff_receivable_line = move.line_ids.filtered(
                    lambda line: line.account_id == payment.destination_account_id)
                invoice_receivable_lines = payment.mapped('invoice_matching_ids.move_id.line_ids').filtered(
                    lambda line: line.account_id == payment.destination_account_id and line.amount_residual)
                if invoice_receivable_lines and writeoff_receivable_line:
                    (invoice_receivable_lines + writeoff_receivable_line).reconcile()

