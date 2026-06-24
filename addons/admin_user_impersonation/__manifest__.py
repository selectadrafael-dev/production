{
    'name': 'Admin User Impersonation',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Allow administrators impersonate users safely',
    'author': 'Custom',
    "author": "Adex",
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_view.xml',
        'views/impersonation_templates.xml',
        'views/res_users_view.xml',
        'views/backend_impersonation_banner.xml',
    ],
    'assets': {
        # 'web.assets_frontend': [
        #     'admin_user_impersonation/static/src/css/impersonation.css',
        # ],
        'web.assets_backend': [
            'admin_user_impersonation/static/src/css/impersonation.css',
        ],
    },
    'installable': True,
    'application': False,
}