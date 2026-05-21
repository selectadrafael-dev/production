{
    'name': 'Product Vendor Visibility',
    'version': '18.0.1.0.0',
    'summary': 'Restrict vendors to their own products',
    'depends': [
        'base',
        'product',
        'website_sale',
    ],
    'data': [
        'security/security.xml',
        'security/product_vendor_rule.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'installable': True,
}