from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPaymentPdcBounce(models.TransientModel):
    _name = 'account.payment.pdc.bounce'
    _description = 'Account Payment PDC Receivable Bounce Wizard'

    payment_id = fields.Many2one(
        comodel_name='account.payment',
        string='PDC',
    )
    bounce_date = fields.Date(
        default=fields.Date.context_today,
    )
    payment_ref = fields.Char(
        string='PDC',
        related='payment_id.ref',
    )
    payment_pdc_state = fields.Selection(
        related='payment_id.pdc_state',
    )
    is_pdc_payable = fields.Boolean(
        string='Is PDC Payable',    related='payment_id.is_pdc_payable',
    )
    allow_merge_pdc = fields.Boolean(
        string='Allow Merge PDC'
    )
    allowed_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_allowed_partner'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Assign To',
    )
    related_payment_ids = fields.Many2many(
        comodel_name='account.payment',
        string='Related PDC',
        domain="[('id', '!=', payment_id),"
               "('pdc_state', '=', payment_pdc_state)]",
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountPaymentPdcBounce, self).default_get(fields)
        if 'active_id' in self.env.context and self.env.context.get(
                'active_model') == 'account.payment':
            payment = self.env['account.payment'].browse(
                self.env.context['active_id'])
            related_payments = self.env['account.payment'].search([
                ('id', '!=', payment.id),
                ('pdc_state', '=', payment.pdc_state),
                ('ref', '=', payment.ref),
                ('company_id', '=', payment.company_id.id),
            ])
            res['payment_id'] = payment.id
            res['partner_id'] = payment.partner_id.id
            if related_payments:
                res['allow_merge_pdc'] = True
                res['related_payment_ids'] = [(6, 0, related_payments.ids)]
        return res

    @api.depends('related_payment_ids', 'payment_id')
    def _compute_allowed_partner(self):
        """
        get all partners can be assigned
        """
        for record in self:
            partners = record.payment_id.partner_id
            for line in record.related_payment_ids:
                partners |= line.partner_id
            record.allowed_partner_ids = partners

    @api.onchange('allow_merge_pdc')
    def _onchange_allow_merge_pdc(self):
        """
        reset data
        """
        if not self.allow_merge_pdc:
            self.partner_id = self.payment_id.partner_id
            self.allowed_partner_ids = False
        else:
            related_payments = self.env['account.payment'].search([
                ('id', '!=', self.payment_id.id),
                ('pdc_state', '=', self.payment_id.pdc_state),
                ('ref', '=', self.payment_id.ref),
                ('company_id', '=', self.payment_id.company_id.id),
            ])
            self.related_payment_ids = related_payments

    def action_bounce_pdc(self):
        """ bounce pdc receivable """
        payment = self.payment_id
        payments = self.env['account.payment']
        if self.related_payment_ids and self.allow_merge_pdc:
            related_pay_journals = self.related_payment_ids.mapped('journal_id')
            if len(related_pay_journals) > 1:
                raise ValidationError(_('Related PDC must have same journal'))
            if related_pay_journals != self.payment_id.journal_id:
                raise ValidationError(_('Related PDC must have journal %s')
                                      % self.payment_id.journal_id.display_name)
            related_pay_state = self.related_payment_ids.mapped('pdc_state')

            if related_pay_state[0] != self.payment_id.pdc_state:
                raise ValidationError(_('Related PDC must has same '
                                        'status as payment %s')
                                      % self.payment_id.display_name)
            related_deposit_journals = self.related_payment_ids.mapped('deposit_pdc_id.bank_journal_id')
            if len(related_deposit_journals) > 1:
                raise ValidationError(_('Related PDC must has same deposit bank'))
            if related_deposit_journals[0] != self.payment_id.deposit_pdc_id.bank_journal_id:
                raise ValidationError(_('Related PDC must has same deposit bank %s')
                                      % self.payment_id.deposit_pdc_id.bank_journal_id.display_name)
            payments = payment + self.related_payment_ids
        else:

            payments = payment
        if all(payments.mapped('is_pdc_payment')):
            payments.action_pdc_receivable_bounced(
                partner=self.partner_id,
                original_payment=self.payment_id,
                related_payments=self.related_payment_ids,
                bounce_date=self.bounce_date,
            )
        if all(payments.mapped('is_pdc_payable')):
            payments.action_pdc_payable_bounced(bounce_date=self.bounce_date)