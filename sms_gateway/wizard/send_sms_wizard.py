from odoo import models, fields, api

class SendSmsWizard(models.TransientModel):
    _name = 'send.sms.wizard'
    _description = 'Send SMS Wizard'

    partner_id = fields.Many2one('res.partner', string='Contact')
    mobile = fields.Char('Mobile')
    message = fields.Text('Message', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model == 'res.partner' and active_id:
            partner = self.env['res.partner'].browse(active_id)
            res.update({'partner_id': partner.id, 'mobile': partner.mobile})
        return res

    def action_send(self):
        api = self.env['sms.api']
        mobiles = [self.mobile]
        result = api.send_sms(mobiles, self.message)
        state = 'sent' if not result.get('error') else 'failed'
        self.env['sms.message'].create({
            'partner_id': self.partner_id.id,
            'mobile': self.mobile,
            'body': self.message,
            'state': state,
            'error': result.get('error'),
            'name': result.get('SMSID'),
            'cost': result.get('Cost'),
            'date_sent': fields.Datetime.now(),
        })
        return {'type': 'ir.actions.act_window_close'}

