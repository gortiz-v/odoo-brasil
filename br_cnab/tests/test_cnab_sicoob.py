# -*- coding: utf-8 -*-
# © 2016 Alessandro Fernandes Martini, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from mock import patch

from odoo.addons.br_cnab.tests.test_cnab_common import TestCnab


class TestCnabSicoob(TestCnab):

    def _return_payment_mode(self):
        super(TestCnabSicoob, self)._return_payment_mode()
        sequencia = self.env['ir.sequence'].create({
            'name': "Nosso Numero"
        })
        sicoob = self.env['res.bank'].search([('bic', '=', '756')])
        conta = self.env['res.partner.bank'].create({
            'acc_number': '12345',  # 5 digitos
            'acc_number_dig': '0',  # 1 digito
            'l10n_br_number': '1234',  # 4 digitos
            'l10n_br_number_dig': '0',
            'codigo_convenio': '123456-7',  # 7 digitos
            'bank_id': sicoob.id,
        })
        mode = self.env['payment.mode'].create({
            'name': 'Sicoob',
            'boleto_type': '9',
            'boleto_carteira': '1',
            'boleto_modalidade': '01',
            'nosso_numero_sequence': sequencia.id,
            'bank_account_id': conta.id
        })
        return mode.id

    @patch('odoo.addons.br_localization_filtering.models.br_localization_filtering.BrLocalizationFiltering._is_user_br_localization')  # noqa  java feelings
    def test_gen_account_move_line(self, br_localization):
        br_localization.return_value = True
        self.invoices.action_invoice_open()
        move = self.invoices.l10n_br_receivable_move_line_ids[0]
        move.action_register_boleto()

        ordem_cobranca = self.env['payment.order'].search([
            ('state', '=', 'draft')
        ], limit=1)
        ordem_cobranca.gerar_cnab()
        cnab = base64.decodestring(ordem_cobranca.cnab_file)
        cnab = cnab.decode('utf-8').split('\r\n')
        cnab.pop()

        self.assertEquals(len(cnab), 7)  # 8 linhas

        for line in cnab:
            self.assertEquals(len(line), 240)  # 8 linhas

        # TODO Descomentar e implementar teste

        # cnab_header_arquivo = cnab[0]
        # cnab_header_lote = cnab[1]
        # cnab_header_arquivo_erros = \
        #     self.sicoob_validate_header_arquivo(cnab_header_arquivo)
        # cnab_header_lote_erros = \
        #     self.sicoob_validate_header_lote(cnab_header_lote)
        # segmentos = cnab[2:-2]
        # dict_segmentos = dict()
        # dict_segmentos['P'] = []
        # dict_segmentos['Q'] = []
        # dict_segmentos['R'] = []
        # for seg in segmentos:
        #     dict_segmentos[seg[13]] += [seg.replace('\r\n', '')]
        #
        # if cnab_header_arquivo_erros != 'SUCESSO':
        #     raise UserError('Header de Arquivo:' + '\n * ' +
        #                     cnab_header_arquivo_erros)
        # elif cnab_header_lote_erros != 'SUCESSO':
        #     raise UserError('Header de Lote:' + '\n * ' +
        #                     cnab_header_lote_erros)
