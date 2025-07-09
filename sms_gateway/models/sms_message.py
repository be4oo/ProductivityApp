from odoo import models, fields

class SmsMessage(models.Model):
    _name = 'sms.message'
    _description = 'SMS Message Log'
    _order = 'create_date desc'

    name = fields.Char('Message ID')
    partner_id = fields.Many2one('res.partner', string='Contact')
    mobile = fields.Char('Mobile')
    body = fields.Text('Message')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ], default='pending')
    error = fields.Text('Error Message')
    cost = fields.Char('Cost')
    date_sent = fields.Datetime('Date Sent')

