# © 2016 Fábio Luna <fabiocluna@hotmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoiceRefund(models.TransientModel):
    _name = 'account.invoice.refund'
    _inherit = ['account.invoice.refund', 'br.localization.filtering']

    l10n_br_fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string="Posição Fiscal")

    @api.multi
    def invoice_refund(self):
        res = super(AccountInvoiceRefund, self).invoice_refund()
        if not self.l10n_br_localization:
            return res
        if type(res) is bool:
            return res
        if "domain" not in res:
            return res

        invoice_id = res['domain'][1][2][0]
        invoice_id = self.env['account.invoice'].search([
            ('id', '=', invoice_id)
        ])
        fiscal_pos = self.l10n_br_fiscal_position_id
        invoice_id.write({
            'fiscal_position_id': fiscal_pos.id,
            'product_serie_id': fiscal_pos.l10n_br_product_serie_id.id,
            'product_document_id': fiscal_pos.l10n_br_product_document_id.id,
            'service_serie_id': fiscal_pos.l10n_br_service_serie_id.id,
            'service_document_id': fiscal_pos.l10n_br_service_document_id.id,
            'fiscal_observation_ids': [(
                6, False, [x.id for x in fiscal_pos.l10n_br_fiscal_observation_ids]
            )]
        })

        if self.l10n_br_fiscal_position_id:
            for item in invoice_id.invoice_line_ids:
                price_unit = item.price_unit
                item._onchange_product_id()
                item._br_account_onchange_product_id()
                item.write({'price_unit': price_unit})
                item._set_extimated_taxes(price_unit)

        return res
