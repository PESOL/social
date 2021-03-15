# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Mail Activity Auto',
    'version': '11.0.1.0.1',
    'author': 'PESOL',
    'website': 'http://pesol.es',
    'category': 'Custom',
    'license': 'AGPL-3',
    'depends': [
        'altiria',
        'crm',
        'mail'
    ],
    'data': [
        'views/mail_activity_type_view.xml',
        'data/mail_activity_cron.xml'
    ],
    'installable': True,
}
