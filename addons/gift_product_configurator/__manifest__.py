{
"name": "Gift Product Configurator",
"version": "18.01.08",
"summary": "Advanced B2B product page for promotional gifts",
"category": "Website",
"author": "SelectAd",
'license': 'LGPL-3',
"depends": [
   'website',
   'website_sale',
   'sale_management'
],
"data": [
    "views/product_page.xml",
    'views/bestsellers_page.xml',
    'views/shop_category_hero.xml',
    #"views/product_components.xml",
    'views/shop_category_hero.xml',
    'views/product_public_category_form.xml',
    'data/sequence.xml',
    'views/quote_drawer_template.xml',
     "views/quote_scripts.xml",
     "views/larger_quantity_template.xml",
     'views/vendor_import_job_views.xml',
     'data/cron.xml',
     'views/res_partner_view.xml'
],
"assets": {
    "web.assets_frontend": [
        "gift_product_configurator/static/src/scss/product_page.scss",
        "gift_product_configurator/static/src/scss/bestsellers.scss",
        "gift_product_configurator/static/src/scss/quote_drawer.scss",
        "gift_product_configurator/static/src/scss/shop_hero.scss",
        "gift_product_configurator/static/src/scss/category_hero.scss",
        "gift_product_configurator/static/src/scss/variants.scss",
        "gift_product_configurator/static/src/scss/larger_quantity.scss",
        "gift_product_configurator/static/src/scss/vendor_tool.scss",
        "gift_product_configurator/static/src/js/configurator.js",
        #"gift_product_configurator/static/src/js/larger_quantity_page.js",
        #"gift_product_configurator/static/src/js/product_update.js",
    ],
},
 'installable': True,
 # ✅ CUSTOM FIELD
'pre_init_hook': 'add_vendor_column',
}
