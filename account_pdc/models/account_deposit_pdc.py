from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountDepositPdc(models.Model):
    _name = 'account.deposit.pdc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Account Deposit PDC'
    _check_company_auto = True
    _order = "deposit_date desc, id desc"


    name = fields.Char(
        string='Number',
        required=True,
        copy=False,
        states={'draft': [('readonly', False)]},
        index=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'New'),
            ('deposit', 'Deposit'),
        ],
        required=True,
        default='draft',
        tracking=True,
    )
    bank_journal_id = fields.Many2one(
        comodel_name='account.journal',
        required=True,
        domain=[('type', '=', 'bank'), ('is_pdc', '=', False)],
        tracking=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        related='bank_journal_id.company_id',
        store=True,
    )
    deposit_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    payment_ids = fields.One2many(
        comodel_name='account.payment',
        inverse_name='deposit_pdc_id',
        string='PDC Receivable',
        check_company=True,
        domain="[('is_pdc_payment','=', True),('payment_type','=', 'inbound'),"
               "('is_internal_transfer','=', False),"
               "('state','=', 'posted'),'&',('deposit_pdc_id','=', False),"
               "('pdc_state','in', ['registered'])]"
    )
    # this field is used to keep track of payment even after return back and create new deposit
    payment_deposit_ids = fields.Many2many(
        comodel_name='account.payment',
    )

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'deposit_date' in vals:
                seq_date = vals['deposit_date']
            vals['name'] = \
                self.env['ir.sequence'].next_by_code('account.deposit.pdc', sequence_date=seq_date) or _('New')
        return super(AccountDepositPdc, self).create(vals)

    def action_deposit(self):
        """ create journal entry for deposit """
        for record in self:
            if not record.payment_ids:
                raise ValidationError(_('Please choose cheque to deposit'))
            record.payment_deposit_ids = record.mapped('payment_ids')
            company_currency = record.bank_journal_id.company_id.currency_id
            for payment in record.payment_ids.filtered(lambda line: line.state == 'posted'):
                payment.mark_as_sent()
                amount_currency = 0
                currency = False
                if payment.currency_id != company_currency:
                    amount_currency = payment._get_payment_amount(company_currency=False)
                    currency = payment.currency_id
                payment_company_amount = payment._get_payment_amount()
                liquidity_analytic_tag_ids = False
                if hasattr(payment, 'liquidity_analytic_tag_ids'):
                    liquidity_analytic_tag_ids = payment.liquidity_analytic_tag_ids.ids
                move = payment._create_pdc_journal_entry(
                    journal=payment.journal_id,
                    partner=payment.partner_id,
                    label='Cheque Deposit %s - %s' % (payment.ref, payment.name),
                    amount=payment_company_amount,
                    debit_account=payment.journal_id.check_under_collection_account_id,
                    credit_account=payment.journal_id.notes_receivable_account_id,
                    amount_currency=amount_currency,
                    currency=currency,
                    ref=payment.name + ' ' + record.name,
                    debit_analytic_tag_ids=liquidity_analytic_tag_ids,
                    credit_analytic_tag_ids=liquidity_analytic_tag_ids,
                    cheque_payment_type='deposit',
                )
                payment.deposit_move_id = move.id
                # payment_line = payment.move_id.line_ids.filtered(
                #     lambda line: line.account_id == payment.journal_id.notes_receivable_account_id)
                # deposit_line = move.line_ids.filtered(
                #     lambda line: line.account_id == payment.journal_id.notes_receivable_account_id)
                # (payment_line + deposit_line).reconcile()
            record.state = 'deposit'
            record.payment_ids.pdc_state = 'deposit'

    def button_open_journal_entry(self):
        """ Redirect the user to journal entry of payments.
        :return:    An action on account.move.
        """
        self.ensure_one()
        moves = self.mapped('payment_ids.deposit_move_id')
        action = {
            'name': _("Journal Entry"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False, 'edit': False},
        }
        if len(moves) == 1:
            action.update({
                'res_id': moves.id,
                'view_mode': 'form',
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'views': [(self.env.ref('account.view_move_tree').id, 'tree'), (False, 'form')],
                'domain': [('id', 'in', moves.ids)],
            })
        return action
