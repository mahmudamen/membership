import ast

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class AccountHandOverPdc(models.Model):
    _name = 'account.hand.over.pdc'
    _description = 'Account Hand Over PDC'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'
    _check_company_auto = True

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: _('New'),
        index=True,
    )
    date = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self),
        copy=False,
    )
    user_from_id = fields.Many2one(
        comodel_name='res.users',
        string='Owner',
        default=lambda self: self.env.user,
        tracking=True,
        required=True,
    )
    user_to_id = fields.Many2one(
        comodel_name='res.users',
        string='Received By',
        tracking=True,
        required=True,
        domain="[('id', '!=', user_from_id)]",
    )
    payment_ids = fields.Many2many(
        comodel_name='account.payment',
        string='PDC',
        copy=False,
        required=True,
        check_company=True,
        domain="[('is_pdc_payment', '=', True),('cheque_owner_id', '=', user_from_id),('pdc_state', '=', 'registered')]",
    )
    reject_reason = fields.Char()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('waiting_approve', 'Waiting Approval'),
            ('hand_over', 'Hand Over'),
            ('reject', 'Rejected'),
        ],
        required=True,
        tracking=True,
        default='draft',
    )
    can_approve = fields.Boolean(
        compute='_compute_can_approve',
        help='Technical field used to hide button based on user to'

    )
    payment_count = fields.Integer(
        compute='_compute_payment_count',
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'company_id' in values:
                self = self.with_company(values['company_id'])
            if values.get('name', _('New')) == _('New'):
                seq_date = None
                if 'date' in values:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(values['date']))
                values['name'] = self.env['ir.sequence'].next_by_code('account.hand.over.pdc',
                                                                      sequence_date=seq_date) or _('New')
        return super(AccountHandOverPdc, self).create(vals_list)

    def _check_hand_over_user(self):
        self.ensure_one()
        payment_issue = self.mapped('payment_ids').filtered(
            lambda pay: pay.pdc_state != 'registered' and self.user_from_id != pay.cheque_owner_id)
        if payment_issue:
            raise ValidationError(
                _('Please remove below PDC(s) that does not registered or hand overed already: \n %(payments)s') % {
                    'payments': '\n'.join(pay.name for pay in payment_issue)
                })

    @api.constrains('payment_ids', 'user_from_id')
    def _constrain_check_payment_owner(self):
        """ restrict to create hand over for another user """
        for record in self:
            if record.payment_ids and record.user_from_id:
                record._check_hand_over_user()

    def _action_notify_users(self, partner_ids, template_param):
        """
        send notification to users
        :param partner_ids:  list (ids) of partner that need to notify
        :param template_param: str config param for email template
        :return:
        """
        for record in self:
            mail_template_id = self.env['ir.config_parameter'].sudo().get_param(template_param, False)
            if not mail_template_id:
                raise ValidationError(_('Please contact administrator to configure template'))
            mail_template = self.env['mail.template'].browse(int(mail_template_id))
            body = mail_template._render_field(
                'body_html', [record.id], compute_lang=True)[record.id]
            subject = mail_template._render_field(
                'subject', [record.id], compute_lang=True)[record.id]
            record.message_post(
                email_from=self.env.user.email_formatted,
                author_id=self.env.user.partner_id.id,
                body=body,
                subject=subject,
                partner_ids=partner_ids,
                force_send=True,
                email_layout_xmlid='mail.message_notification_email',
                message_type='comment',
            )

    def action_submit(self):
        """ update status and send notification to user to approve """
        template_param = 'account_pdc.default_notify_hand_over_template'
        for record in self:
            record._check_hand_over_user()
            record.write({'state': 'waiting_approve'})
            partner = record.user_to_id.partner_id if record.user_to_id else False
            if partner:
                record._action_notify_users(partner_ids=partner.ids, template_param=template_param)

    def action_approve(self):
        """ update status and change owner of pdc """
        self.write({'state': 'hand_over'})
        for record in self:
            payment_issue = record.mapped('payment_ids').filtered(
                lambda pay: pay.pdc_state != 'registered' and record.user_from_id != pay.cheque_owner_id)
            if payment_issue:
                raise ValidationError(
                    _('You can not hand over below PDC(s) that does not registered or hand overed already, '
                      'Please reject request:\n %(payments)s') % {
                        'payments': '\n'.join(pay.name for pay in payment_issue)
                    })
            record.mapped('payment_ids').write({'cheque_owner_id': record.user_to_id.id})

    def action_reject(self, reason=''):
        """ update status and notify original user """
        self.write({'state': 'reject', 'reject_reason': reason})
        template_param = 'account_pdc.default_notify_hand_over_reject_template'
        for record in self:
            partner = record.user_from_id.partner_id if record.user_from_id else False
            if partner:
                self._action_notify_users(partner_ids=partner.ids, template_param=template_param)

    def action_reset_draft(self):
        """ reset request to draft """
        self.write({'state': 'draft'})

    @api.onchange('user_from_id')
    def _onchange_user_from(self):
        """ reset payment to force user choose new payments """
        self.payment_ids = [fields.Command.clear()]

    @api.depends_context('uid')
    @api.depends('user_to_id')
    def _compute_can_approve(self):
        """ return true if current user is open form """
        current_user = self.env.user
        for record in self:
            can_approve = False
            if record.user_to_id == current_user:
                can_approve = True
            record.can_approve = can_approve

    def action_open_pdc_receivable(self):
        """
        open related pdc receivable
        :return: action
        """

        payments = self.mapped('payment_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account_pdc.account_payment_pdc_receivable_action")
        if len(payments) > 1:
            action['domain'] = [('id', 'in', payments.ids)]
        elif len(payments) == 1:
            form_view = [(self.env.ref('account_pdc.account_payment_pdc_receivable_form_inherit_primary').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = payments.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        action['context'] = dict(ast.literal_eval(action['context']), create=False)
        return action

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        """ count number of payment """
        for record in self:
            record.payment_count = len(record.payment_ids) if record.payment_ids else 0
