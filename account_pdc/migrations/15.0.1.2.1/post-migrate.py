from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    payments = env['account.payment'].search(
        ['|', ('is_pdc_payment', '=', True), ('is_pdc_payable', '=', True)])
    for payment in payments:
        if payment.deposit_move_id:
            payment.deposit_move_id.cheque_payment_type = 'deposit'
        if payment.collect_payment_id:
            payment.collect_payment_id.cheque_payment_type = 'collected'
        if payment.bounced_move_id:
            payment.bounced_move_id.cheque_payment_type = 'bounced'
        if payment.cleared_pdc_payable_move_id:
            payment.cleared_pdc_payable_move_id.cheque_payment_type = 'cleared'
        if payment.cash_payment_id:
            payment.cash_payment_id.move_id.cheque_payment_type = 'cashed'
        if payment.write_off_payment_id:
            payment.write_off_payment_id.move_id.cheque_payment_type = 'writeoff'
        if payment.recheque_payment_id:
            payment.recheque_payment_id.move_id.cheque_payment_type = 'recheque'
        for move in payment.cheque_move_ids.filtered(
                lambda m: not m.cheque_payment_type):
            if move.payment_id.payment_type == 'inbound':
                move.cheque_payment_type = 'bounced_in'
            if move.payment_id.payment_type == 'outbound':
                move.cheque_payment_type = 'bounced_out'
    #  we need to make sure that all moves has type,
    #  so we should match with label of journal items
    related_moves = env['account.move'].search(
        [('cheque_payment_id', '!=', False),
         ('cheque_payment_type', '=', False)])
    for move in related_moves:
        if 'Cheque Deposit' in str(move.line_ids.mapped('name')):
            move.cheque_payment_type = 'deposit'
        if 'Bounce' in move.ref and move.payment_id.payment_type == 'inbound':
            move.cheque_payment_type = 'bounced_in'
        if 'Bounce' in move.ref and move.payment_id.payment_type == 'outbound':
            move.cheque_payment_type = 'bounced_out'
    # if hasattr(env['account.payment'], 'liquidity_analytic_tag_ids'):
        # for payment in payments:
            # liquidity_analytic_tags = payment.liquidity_analytic_tag_ids
            # counterpart_analytic_tags = payment.counterpart_analytic_tag_ids
            # if payment.cheque_move_ids:
                # for move in payment.cheque_move_ids:
                    # if move.cheque_payment_type in ['writeoff']:
                    #     payment_lines = move.line_ids.filtered(
                    #         lambda line: line.account_id ==
                    #                      move.payment_id.outstanding_account_id)
                    #     payment_lines.with_context(
                    #         skip_account_move_synchronization=True
                    #     ).write({
                    #         'analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)]
                    #     })
                    #     move.payment_id.with_context(
                    #         skip_account_move_synchronization=True
                    #     ).write({
                    #         'liquidity_analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)]
                    #     })
                    # if move.cheque_payment_type in ['recheque', 'cashed']:
                    #     # @formatter:off
                    #     payment_lines = move.line_ids.filtered(
                    #         lambda line: line.account_id ==
                    #         move.payment_id.outstanding_account_id)
                    #     counterpart_lines = move.line_ids.filtered(
                    #         lambda line: line.account_id ==
                    #         move.payment_id.destination_account_id)
                    #     # @formatter:on
                    #     payment_lines.with_context(
                    #         skip_account_move_synchronization=True).write({
                    #         'analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)]
                    #     })
                    #     counterpart_lines.with_context(
                    #         skip_account_move_synchronization=True).write({
                    #         'analytic_tag_ids': [
                    #             (6, 0, counterpart_analytic_tags.ids)]
                    #     })
                    #     move.payment_id.with_context(
                    #         skip_account_move_synchronization=True).write({
                    #         'liquidity_analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)],
                    #         'counterpart_analytic_tag_ids': [
                    #             (6, 0, counterpart_analytic_tags.ids)]
                    #     })
                    # if move.cheque_payment_type in ['bounced_in', 'bounced_out', 'collected', 'bounced', 'deposit', 'cleared']:
                    #     move.line_ids.with_context(skip_account_move_synchronization=True).write({
                    #         'analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)]
                    #     })
                    #     move.payment_id.with_context(skip_account_move_synchronization=True).write({
                    #         'liquidity_analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)],
                    #         'counterpart_analytic_tag_ids': [
                    #             (6, 0, liquidity_analytic_tags.ids)]
                    #     })

