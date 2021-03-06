# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

from openerp import models, api

TICKET_FROM = 'ecino@compassion.com'
TICKET_TO = 'compassion@service-now.com'
TICKET_CC = 'YBoska@us.ci.org'


class ResPartner(models.Model):
    """ Send tickets to GMC in case of change of 'send_original'
    parameter
    """
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        partner = super(ResPartner, self).create(vals)
        if partner.send_original:
            partner._send_ticket(partner.send_original)
        return partner

    @api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'send_original' in vals:
            self._send_ticket(vals['send_original'])
        return res

    def _send_ticket(self, send_original):
        """ Send ticket to GMC to request or cancel sending original
        letters of child. """
        if send_original:
            template = self.env.ref('sbc_email.ticket_send_original')
        else:
            template = self.env.ref(
                'sbc_email.ticket_block_original')
        # Create and send email
        email_vals = {
            'email_to': TICKET_TO,
            'email_from': TICKET_FROM,
            'email_cc': TICKET_CC
        }
        for partner in self:
            self.env['mail.compose.message'].with_context(
                lang=partner.lang).create_emails(
                template, partner.id, email_vals).send_sendgrid()
