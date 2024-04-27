from datetime import date

from odoo import _, fields, models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    cheque_payment_id = fields.Many2one(
        comodel_name='account.payment',
        copy=False,
    )

    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
                               states={'draft': [('readonly', False)]}, default=fields.Date.context_today)

    is_pdc_receivable_entry = fields.Boolean(string='Is PDC Receivable Entry', readonly=True, store=True)

    cheque_payment_type = fields.Selection(
        selection=[('bounced', 'Bounced'),
                   ('deposit', 'Deposit'),
                   ('collected', 'Collected'),
                   ('delivered', 'Delivered'),
                   ('received', 'Received'),
                   ('cleared', 'Cleared'),
                   ('writeoff', 'Write-off'),
                   ('recheque', 'Recheque'),
                   ('bounced_in', 'Bounced In Bank'),
                   ('bounced_out', 'Bounced Out Bank'),
                   ('cashed', 'Cashed'),
                   ('recycled', 'Recycled'),
                   ('collection_fees', 'Collection Fees'),
                   ],
    )

    @api.model
    def _search_default_journal(self, journal_types):
        """ handle case default from pdc receivable """
        journal = super()._search_default_journal(journal_types)
        if self.env.context.get('default_is_pdc_payment'):
            company_id = self._context.get('default_company_id', self.env.company.id)
            domain = [('company_id', '=', company_id), ('is_pdc', '=', True), ('type', '=', 'bank')]
            journal = self.env['account.journal'].search(domain, limit=1)
        if self.env.context.get('default_is_pdc_payable'):
            company_id = self._context.get('default_company_id', self.env.company.id)
            domain = [('company_id', '=', company_id),
                      ('notes_payable_account_id', '!=', False),
                      ('type', '=', 'bank')]
            journal = self.env['account.journal'].search(domain, limit=1)
        return journal

    def action_open_related_pdc(self):
        """
        open pdc receivable cashed payments
        """
        self.ensure_one()
        cheque_payment = self.cheque_payment_id
        action = {
            'name': _("PDC"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'context': {'create': False, 'edit': False},
            'res_id': cheque_payment.id,
            'view_mode': 'form',
        }
        return action


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_pdc_receivable_entry = fields.Boolean(string='Is PDC Receivable Entry', readonly=True, store=True)

    def _create_exchange_difference_move(self):
        ''' Create the exchange difference journal entry on the current journal items.
        :return: An account.move record.
        '''

        def _add_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
            ''' Generate the exchange difference values used to create the journal items
            in order to fix the residual amounts and add them into 'exchange_diff_move_vals'.

            1) When reconciled on the same foreign currency, the journal items are
            fully reconciled regarding this currency but it could be not the case
            of the balance that is expressed using the company's currency. In that
            case, we need to create exchange difference journal items to ensure this
            residual amount reaches zero.

            2) When reconciled on the company currency but having different foreign
            currencies, the journal items are fully reconciled regarding the company
            currency but it's not always the case for the foreign currencies. In that
            case, the exchange difference journal items are created to ensure this
            residual amount in foreign currency reaches zero.

            :param lines:                   The account.move.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            :return:                        A list of pair <line, sequence> to perform the reconciliation
                                            at the creation of the exchange difference move where 'line'
                                            is the account.move.line to which the 'sequence'-th exchange
                                            difference line will be reconciled with.
            '''
            journal = self.env['account.journal'].browse(exchange_diff_move_vals['journal_id'])
            to_reconcile = []

            for line in lines:

                exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], line.date)

                if not line.company_currency_id.is_zero(line.amount_residual):
                    # amount_residual_currency == 0 and amount_residual has to be fixed.

                    if line.amount_residual > 0.0:
                        exchange_line_account = journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account = journal.company_id.income_currency_exchange_account_id

                elif line.currency_id and not line.currency_id.is_zero(line.amount_residual_currency):
                    # amount_residual == 0 and amount_residual_currency has to be fixed.

                    if line.amount_residual_currency > 0.0:
                        exchange_line_account = journal.company_id.expense_currency_exchange_account_id
                    else:
                        exchange_line_account = journal.company_id.income_currency_exchange_account_id
                else:
                    continue

                sequence = len(exchange_diff_move_vals['line_ids'])
                exchange_diff_move_vals['line_ids'] += [
                    (0, 0, {
                        'name': _('Currency exchange rate difference'),
                        'debit': -line.amount_residual if line.amount_residual < 0.0 else 0.0,
                        'credit': line.amount_residual if line.amount_residual > 0.0 else 0.0,
                        'amount_currency': -line.amount_residual_currency,
                        'account_id': line.account_id.id,
                        'currency_id': line.currency_id.id,
                        'partner_id': line.partner_id.id,
                        'sequence': sequence,
                    }),
                    (0, 0, {
                        'name': _('Currency exchange rate difference'),
                        'debit': line.amount_residual if line.amount_residual > 0.0 else 0.0,
                        'credit': -line.amount_residual if line.amount_residual < 0.0 else 0.0,
                        'amount_currency': line.amount_residual_currency,
                        'account_id': exchange_line_account.id,
                        'currency_id': line.currency_id.id,
                        'partner_id': line.partner_id.id,
                        'sequence': sequence + 1,
                    }),
                ]

                to_reconcile.append((line, sequence))

            return to_reconcile

        def _add_cash_basis_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
            ''' Generate the exchange difference values used to create the journal items
            in order to fix the cash basis lines using the transfer account in a multi-currencies
            environment when this account is not a reconcile one.

            When the tax cash basis journal entries are generated and all involved
            transfer account set on taxes are all reconcilable, the account balance
            will be reset to zero by the exchange difference journal items generated
            above. However, this mechanism will not work if there is any transfer
            accounts that are not reconcile and we are generating the cash basis
            journal items in a foreign currency. In that specific case, we need to
            generate extra journal items at the generation of the exchange difference
            journal entry to ensure this balance is reset to zero and then, will not
            appear on the tax report leading to erroneous tax base amount / tax amount.

            :param lines:                   The account.move.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            '''
            for move in lines.move_id:
                account_vals_to_fix = {}

                move_values = move._collect_tax_cash_basis_values()

                # The cash basis doesn't need to be handle for this move because there is another payment term
                # line that is not yet fully paid.
                if not move_values or not move_values['is_fully_paid']:
                    continue

                # ==========================================================================
                # Add the balance of all tax lines of the current move in order in order
                # to compute the residual amount for each of them.
                # ==========================================================================

                for caba_treatment, line in move_values['to_process_lines']:

                    vals = {
                        'currency_id': line.currency_id.id,
                        'partner_id': line.partner_id.id,
                        'tax_ids': [(6, 0, line.tax_ids.ids)],
                        'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)],
                        'debit': line.debit,
                        'credit': line.credit,
                    }

                    if caba_treatment == 'tax':
                        # Tax line.
                        grouping_key = self.env[
                            'account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(line)
                        if grouping_key in account_vals_to_fix:
                            debit = account_vals_to_fix[grouping_key]['debit'] + vals['debit']
                            credit = account_vals_to_fix[grouping_key]['credit'] + vals['credit']
                            balance = debit - credit

                            account_vals_to_fix[grouping_key].update({
                                'debit': balance if balance > 0 else 0,
                                'credit': -balance if balance < 0 else 0,
                                'tax_base_amount': account_vals_to_fix[grouping_key][
                                                       'tax_base_amount'] + line.tax_base_amount,
                            })
                        else:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                'account_id': line.account_id.id,
                                'tax_base_amount': line.tax_base_amount,
                                'tax_repartition_line_id': line.tax_repartition_line_id.id,
                            }
                    elif caba_treatment == 'base':
                        # Base line.
                        account_to_fix = line.company_id.account_cash_basis_base_account_id
                        if not account_to_fix:
                            continue

                        grouping_key = self.env[
                            'account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(line,
                                                                                                            account=account_to_fix)

                        if grouping_key not in account_vals_to_fix:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                'account_id': account_to_fix.id,
                            }
                        else:
                            # Multiple base lines could share the same key, if the same
                            # cash basis tax is used alone on several lines of the invoices
                            account_vals_to_fix[grouping_key]['debit'] += vals['debit']
                            account_vals_to_fix[grouping_key]['credit'] += vals['credit']

                # ==========================================================================
                # Subtract the balance of all previously generated cash basis journal entries
                # in order to retrieve the residual balance of each involved transfer account.
                # ==========================================================================

                cash_basis_moves = self.env['account.move'].search([('tax_cash_basis_origin_move_id', '=', move.id)])
                for line in cash_basis_moves.line_ids:
                    grouping_key = None
                    if line.tax_repartition_line_id:
                        # Tax line.
                        grouping_key = self.env[
                            'account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(
                            line,
                            account=line.tax_line_id.cash_basis_transition_account_id,
                        )
                    elif line.tax_ids:
                        # Base line.
                        grouping_key = self.env[
                            'account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(
                            line,
                            account=line.company_id.account_cash_basis_base_account_id,
                        )

                    if grouping_key not in account_vals_to_fix:
                        continue

                    account_vals_to_fix[grouping_key]['debit'] -= line.debit
                    account_vals_to_fix[grouping_key]['credit'] -= line.credit

                # ==========================================================================
                # Generate the exchange difference journal items:
                # - to reset the balance of all transfer account to zero.
                # - fix rounding issues on the tax account/base tax account.
                # ==========================================================================

                for values in account_vals_to_fix.values():
                    balance = values['debit'] - values['credit']

                    if move.company_currency_id.is_zero(balance):
                        continue

                    if values.get('tax_repartition_line_id'):
                        # Tax line.
                        tax_repartition_line = self.env['account.tax.repartition.line'].browse(
                            values['tax_repartition_line_id'])
                        account = tax_repartition_line.account_id or self.env['account.account'].browse(
                            values['account_id'])

                        sequence = len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids'] += [
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': balance if balance > 0.0 else 0.0,
                                'credit': -balance if balance < 0.0 else 0.0,
                                'account_id': account.id,
                                'sequence': sequence,
                            }),
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': -balance if balance < 0.0 else 0.0,
                                'credit': balance if balance > 0.0 else 0.0,
                                'account_id': values['account_id'],
                                'tax_ids': [],
                                'tax_tag_ids': [],
                                'tax_repartition_line_id': False,
                                'sequence': sequence + 1,
                            }),
                        ]
                    else:
                        # Base line.
                        sequence = len(exchange_diff_move_vals['line_ids'])
                        exchange_diff_move_vals['line_ids'] += [
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': balance if balance > 0.0 else 0.0,
                                'credit': -balance if balance < 0.0 else 0.0,
                                'sequence': sequence,
                            }),
                            (0, 0, {
                                **values,
                                'name': _('Currency exchange rate difference (cash basis)'),
                                'debit': -balance if balance < 0.0 else 0.0,
                                'credit': balance if balance > 0.0 else 0.0,
                                'tax_ids': [],
                                'tax_tag_ids': [],
                                'sequence': sequence + 1,
                            }),
                        ]

        if not self:
            return self.env['account.move']

        company = self[0].company_id
        journal = company.currency_exchange_journal_id

        exchange_diff_move_vals = {
            'move_type': 'entry',
            'date': date.min,
            'journal_id': journal.id,
            'line_ids': [],
        }

        # Fix residual amounts.
        to_reconcile = _add_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

        # Fix cash basis entries.
        is_cash_basis_needed = self[0].account_internal_type in ('receivable', 'payable')
        if is_cash_basis_needed:
            _add_cash_basis_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

        # ==========================================================================
        # Create move and reconcile.
        # ==========================================================================

        if exchange_diff_move_vals['line_ids']:
            # Check the configuration of the exchange difference journal.
            if not journal:
                raise UserError(
                    _("You should configure the 'Exchange Gain or Loss Journal' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not journal.company_id.expense_currency_exchange_account_id:
                raise UserError(
                    _("You should configure the 'Loss Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not journal.company_id.income_currency_exchange_account_id.id:
                raise UserError(
                    _("You should configure the 'Gain Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))

            exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], company._get_user_fiscal_lock_date())

            # exchange_move = self.env['account.move'].create(exchange_diff_move_vals)
            exchange_move = False
        else:
            return None

        # Reconcile lines to the newly created exchange difference journal entry by creating more partials.
        partials_vals_list = []
        if exchange_move:
            for source_line, sequence in to_reconcile:
                exchange_diff_line = exchange_move.line_ids[sequence]

                if source_line.company_currency_id.is_zero(source_line.amount_residual):
                    exchange_field = 'amount_residual_currency'
                else:
                    exchange_field = 'amount_residual'

                if exchange_diff_line[exchange_field] > 0.0:
                    debit_line = exchange_diff_line
                    credit_line = source_line
                else:
                    debit_line = source_line
                    credit_line = exchange_diff_line

                partials_vals_list.append({
                    'amount': abs(source_line.amount_residual),
                    'debit_amount_currency': abs(debit_line.amount_residual_currency),
                    'credit_amount_currency': abs(credit_line.amount_residual_currency),
                    'debit_move_id': debit_line.id,
                    'credit_move_id': credit_line.id,
                })

            self.env['account.partial.reconcile'].create(partials_vals_list)
        return exchange_move

    def reconcile(self):
        """
        inherit to unmark is_pdc_receivable_entry
        """
        res = super(AccountMoveLine, self).reconcile()
        if res.get('partials'):
            reconciled = res.get('partials')
            for move in reconciled:
                for line in move.debit_move_id.filtered(lambda m:m.move_id.cheque_payment_id):
                    pdc = line.move_id.cheque_payment_id
                    if pdc:
                        pdc.move_id.line_ids.is_pdc_receivable_entry = False

        return res
