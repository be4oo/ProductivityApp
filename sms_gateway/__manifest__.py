{
    'name': 'SMS Gateway Integration',
    'version': '1.0',
    'summary': 'Integrate Odoo with SMSMisr and SMSVAS providers',
    'author': 'Generated',
    'website': 'http://example.com',
    'category': 'Tools',
    'depends': ['base', 'contacts', 'sale_management', 'crm', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_message_views.xml',
        'views/sms_settings_views.xml',
        'views/res_partner_views.xml',
        'views/send_sms_action.xml',
        'data/sms_template.xml',
        'views/send_sms_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}

