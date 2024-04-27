from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_pdc = fields.Boolean(
        string='Use PDC Receivable',
    )
    notes_receivable_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Notes Receivable Account',
        check_company=True,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id),('reconcile', '=', True), \
                              ('user_type_id.type', 'not in', ('receivable', 'payable')), ('user_type_id', 'in', %s)]"
                            % [self.env.ref('account.data_account_type_current_assets').id],
    )
    check_under_collection_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Check Under Collection Account',
        check_company=True,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), ('reconcile', '=', True), \
                              ('user_type_id.type', 'not in', ('receivable', 'payable')), ('user_type_id', 'in', %s)]"
                            % [self.env.ref('account.data_account_type_current_assets').id],
    )
    write_off_pdc_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Write Off Account',
        check_company=True,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                              ('user_type_id.type', 'not in', ('receivable', 'payable')), ('user_type_id', 'in', %s)]"
                            % [self.env.ref('account.data_account_type_expenses').id],
    )
    notes_payable_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Notes Payable Account',
        check_company=True,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id),('reconcile', '=', True), \
                                      ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                                      ('user_type_id', 'in', %s)]"
                            % [self.env.ref('account.data_account_type_current_liabilities').id],
    )
    pdc_payable_under_collection_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Under Collection Payable Account',
        check_company=True,
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id),('reconcile', '=', True), \
                                               ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                                               ('user_type_id', 'in', %s)]"
                            % [self.env.ref('account.data_account_type_current_liabilities').id],
    )

    @api.onchange('type')
    def _onchange_type(self):
        """ reset is pdc if type is not bank """
        super(AccountJournal, self)._onchange_type()
        if self.type != 'bank':
            self.is_pdc = False
            self.notes_payable_account_id = False
