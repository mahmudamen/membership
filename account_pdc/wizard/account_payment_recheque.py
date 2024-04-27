from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountPaymentReCheque(models.TransientModel):
    _name = 'account.payment.recheque'
    _description = 'Account Payment Re Cheque Wizard'

    pdc_bank_id = fields.Many2one(
        comodel_name='res.bank',
        string='Bank Name',
    )
    cheque_number = fields.Char(
        required=True,
    )
    due_date = fields.Date(
        required=True,
    )
    cheque_scanning = fields.Binary(
        required=True,
    )
    cheque_owner_id = fields.Many2one(
        comodel_name='res.users',
        default=lambda self: self.env.user,
        required=True,
    )

    def action_recheque(self):
        """ convert payment to another cheque and cancel old cheque """
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model != 'account.payment':
            raise ValidationError(_('Please open Cheque'))

        payment = self.env[active_model].browse(active_id)
        if payment.is_pdc_payment:
            reconciled_invoice_ids = payment.reconciled_invoice_ids
            # payment.with_context(force_reset_draft=True).action_draft()
            # payment.action_cancel()
            payment.pdc_state = 're_cheque'
            # payment.move_id.mapped('line_ids').remove_move_reconcile()
            if reconciled_invoice_ids:
                vals = {
                    'amount': payment._get_payment_amount(company_currency=False),
                    'communication': self.cheque_number,
                    'currency_id': payment.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.journal_id.id,
                    'payment_method_line_id': payment.payment_method_line_id.id,
                    'pdc_bank_id': self.pdc_bank_id.id if self.pdc_bank_id else False,
                    'due_date': self.due_date,
                    'cheque_scanning': self.cheque_scanning,
                    'cheque_owner_id': self.cheque_owner_id.id,
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
                    default_cheque_payment_type='recheque',
                    default_cheque_payment_id=payment.id
                ).create(vals)
                new_payment = payment_wizard._create_payments()
            else:
                vals = {
                    'amount': payment._get_payment_amount(company_currency=False),
                    'ref': self.cheque_number,
                    'currency_id': payment.currency_id.id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.journal_id.id,
                    'payment_method_line_id': payment.payment_method_line_id.id,
                    'pdc_bank_id': self.pdc_bank_id.id if self.pdc_bank_id else False,
                    'due_date': self.due_date,
                    'cheque_scanning': self.cheque_scanning,
                    'cheque_owner_id': self.cheque_owner_id.id,
                    'company_id': payment.journal_id.company_id.id,
                    'cheque_payment_id': payment.id,
                    'date': fields.Date.context_today(payment),
                    'cheque_payment_type': 'recheque',
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
                            self.env['account.payment.invoice.matching'].create(data)
                        new_invoice_match._compute_invoice_amount()
                new_payment.action_post()

            new_payment.move_id.cheque_payment_id = payment
            payment.recheque_payment_id = new_payment
            action = {
                'name': _('Payments'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'context': {'create': False},
                'view_mode': 'form',
                'res_id': new_payment.id,
                'views': [(self.env.ref('account_pdc.account_payment_pdc_receivable_form_inherit_primary').id, 'form')],
            }
            return action
