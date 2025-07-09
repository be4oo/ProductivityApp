import logging
import requests
from odoo import models, fields, _

_logger = logging.getLogger(__name__)

class SmsApi(models.AbstractModel):
    _name = 'sms.api'
    _description = 'SMS API Integration'

    def _get_provider_config(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        provider = ir_config.get_param('sms_gateway.provider', 'smsmisr')
        username = ir_config.get_param('sms_gateway.username')
        password = ir_config.get_param('sms_gateway.password')
        sender = ir_config.get_param('sms_gateway.sender')
        api_url = ir_config.get_param('sms_gateway.api_url')
        return provider, username, password, sender, api_url

    def send_sms(self, mobiles, message, language=1):
        provider, username, password, sender, api_url = self._get_provider_config()
        if provider == 'smsmisr':
            return self._send_sms_misr(api_url, username, password, sender, mobiles, message, language)
        elif provider == 'smsvas':
            return self._send_sms_vas(api_url, username, password, sender, mobiles, message, language)
        else:
            return {'error': _('Unknown SMS provider')}

    def _send_sms_misr(self, url, username, password, sender, mobiles, message, language):
        params = {
            'environment': 2,  # testing
            'username': username,
            'password': password,
            'sender': sender,
            'mobile': ','.join(mobiles),
            'language': language,
            'message': message,
        }
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.exception('SMSMisr send failed: %s', e)
            return {'error': str(e)}

    def _send_sms_vas(self, url, username, password, sender, mobiles, message, language):
        payload = {
            'Username': username,
            'Password': password,
            'SenderName': sender,
            'ReceiverMSISDN': ','.join(mobiles),
            'SMSText': message,
            'SMSType': language,
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _logger.exception('SMSVAS send failed: %s', e)
            return {'error': str(e)}

