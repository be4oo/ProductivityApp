from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sms_provider = fields.Selection([
        ('smsmisr', 'SMSMisr'),
        ('smsvas', 'SMSVAS')
    ], string='SMS Provider', default='smsmisr')
    sms_username = fields.Char('SMS Username')
    sms_password = fields.Char('SMS Password')
    sms_sender = fields.Char('SMS Sender ID')
    sms_api_url = fields.Char('API URL')

    def set_values(self):
        res = super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('sms_gateway.provider', self.sms_provider or '')
        self.env['ir.config_parameter'].sudo().set_param('sms_gateway.username', self.sms_username or '')
        self.env['ir.config_parameter'].sudo().set_param('sms_gateway.password', self.sms_password or '')
        self.env['ir.config_parameter'].sudo().set_param('sms_gateway.sender', self.sms_sender or '')
        self.env['ir.config_parameter'].sudo().set_param('sms_gateway.api_url', self.sms_api_url or '')
        return res

    def get_values(self):
        res = super().get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        res.update(
            sms_provider=ir_config.get_param('sms_gateway.provider', default='smsmisr'),
            sms_username=ir_config.get_param('sms_gateway.username', default=''),
            sms_password=ir_config.get_param('sms_gateway.password', default=''),
            sms_sender=ir_config.get_param('sms_gateway.sender', default=''),
            sms_api_url=ir_config.get_param('sms_gateway.api_url', default=''),
        )
        return res

