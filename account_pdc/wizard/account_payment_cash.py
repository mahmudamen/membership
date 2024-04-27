from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountPaymentCash(models.TransientModel):
    _name = 'account.payment.cash'
    _description = 'Account Payment Cash Wizard'

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        required=True,
        domain="[('type', '=', 'cash')]",
    )
    available_payment_method_line_ids = fields.Many2many(
        'account.payment.method.line',
        compute='_compute_payment_method_line_fields')
    hide_payment_method_line = fields.Boolean(
        compute='_compute_payment_method_line_fields',
        help="Technical field used to hide the payment method if the selected journal has only one available which "
             "is 'manual'")

    payment_method_line_id = fields.Many2one(
        'account.payment.method.line', string='Payment Method',
        readonly=False, store=True,
        compute='_compute_payment_method_line_id',
        domain="[('id', 'in', available_payment_method_line_ids)]",
        help="Manual: Pay or Get paid by any method outside of Odoo.\n"
             "Payment Acquirers: Each payment acquirer has its own Payment Method. Request a transaction on/to "
             "a card thanks to a payment token saved by the partner when buying or subscribing online.\n"
             "Check: Pay bills by check and print it from Odoo.\n"
             "Batch Deposit: Collect several customer checks at once generating and submitting a batch deposit "
             "to your bank. Module account_batch_payment is necessary.\n"
             "SEPA Credit Transfer: Pay in the SEPA zone by submitting a SEPA Credit Transfer file to your bank."
             " Module account_sepa is necessary.\n"
             "SEPA Direct Debit: Get paid in the SEPA zone thanks to a mandate your partner will have granted to you."
             " Module account_sepa is necessary.\n")

    @api.depends('journal_id')
    def _compute_payment_method_line_id(self):
        for wizard in self:
            available_payment_method_lines = wizard.journal_id._get_available_payment_method_lines('inbound')

            # Select the first available one by default.
            if available_payment_method_lines:
                wizard.payment_method_line_id = available_payment_method_lines[0]._origin
            else:
                wizard.payment_method_line_id = False

    @api.depends('journal_id')
    def _compute_payment_method_line_fields(self):
        for wizard in self:
            wizard.available_payment_method_line_ids = wizard.journal_id._get_available_payment_method_lines('inbound')
            if wizard.payment_method_line_id.id not in wizard.available_payment_method_line_ids.ids:
                # In some cases, we could be linked to a payment method line that has been unlinked from the journal.
                # In such cases, we want to show it on the payment.
                wizard.hide_payment_method_line = False
            else:
                wizard.hide_payment_method_line = len(wizard.available_payment_method_line_ids) == 1 \
                                                  and wizard.available_payment_method_line_ids.code == 'manual'

    def action_register_payment(self):
        """ convert payment to cash and cancel cheque """
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model != 'account.payment':
            raise ValidationError(_('Please open Cheque'))

        payment = self.env[active_model].browse(active_id)
        if payment.is_pdc_payment:
            reconciled_invoice_ids = payment.reconciled_invoice_ids
            # payment.action_draft()
            # payment.action_cancel()
            self._reverse_original_pdc(payment)
            payment.pdc_state = 'cashed'
            payment.move_id.mapped('line_ids').remove_move_reconcile()
            if reconciled_invoice_ids:
                vals = {
                    'amount': payment._get_payment_amount(company_currency=False),
                    'communication': 'Cheque Info ' + payment.name + ' - ' + payment.ref,
                    'currency_id': payment.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': payment.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'payment_method_line_id': self.payment_method_line_id.id,
                }
                # if hasattr(self.env['account.payment.register'], 'liquidity_analytic_tag_ids'):
                #     vals.update({
                #         'liquidity_analytic_tag_ids': [(6, 0, payment.liquidity_analytic_tag_ids.ids)],
                #         'counterpart_analytic_tag_ids': [(6, 0, payment.counterpart_analytic_tag_ids.ids)]
                #     })
                if len(reconciled_invoice_ids) > 1:
                    vals.update({
                        'group_payment': True,
                    })
                payment_wizard = self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=reconciled_invoice_ids.ids,
                    default_cheque_payment_type='cashed',
                    default_cheque_payment_id=payment.id
                ).create(vals)
                new_payment = payment_wizard._create_payments()
            else:
                vals = {
                    'amount': payment._get_payment_amount(company_currency=False),
                    'ref': f'Cheque Info {payment.name if payment.name else ""}  -  {payment.ref if payment.ref else "" }',
                    'currency_id': payment.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': payment.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'payment_method_line_id': self.payment_method_line_id.id,
                    'company_id': self.journal_id.company_id.id,
                    'date': fields.Date.context_today(payment),
                    'cheque_payment_type': 'cashed',
                    'cheque_payment_id': payment.id,
                }
                # if hasattr(payment, 'liquidity_analytic_tag_ids'):
                #     vals.update({
                #         'liquidity_analytic_tag_ids': [(6, 0, payment.liquidity_analytic_tag_ids.ids)],
                #         'counterpart_analytic_tag_ids': [(6, 0, payment.counterpart_analytic_tag_ids.ids)]
                #     })
                new_payment = self.env['account.payment'].create(vals)
                if hasattr(payment, 'invoice_matching_ids'):
                    for invoice_match in payment.invoice_matching_ids:
                        data = invoice_match.copy_data({
                            'payment_id': new_payment.id,
                        })
                        new_invoice_match = \
                            self.env['account.payment.invoice.matching'].create(
                                data)
                        new_invoice_match._compute_invoice_amount()
                new_payment.action_post()

            new_payment.move_id.cheque_payment_id = payment
            payment.cash_payment_id = new_payment
            action = {
                'name': _('Payments'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'context': {'create': False},
                'view_mode': 'form',
                'res_id': new_payment.id,
                'views': [(self.env.ref(
                    'account.view_account_payment_form').id,
                           'form')],
            }
            return action
    def _reverse_original_pdc(self, payments):
        """
        reverse pdc journal entry
        """
        for payment in payments:
            if payment.pdc_state == 'registered':
                default_values_list = [{
                    'cheque_payment_id': payment.id,
                }]
                reverse_move = payment.move_id._reverse_moves(
                    default_values_list=default_values_list, cancel=True)
                payment.related_move_ids |= reverse_move
