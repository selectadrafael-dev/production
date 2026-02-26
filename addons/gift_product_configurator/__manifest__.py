{
"name": "Gift Product Configurator",
"version": "18.01.08",
"summary": "Advanced B2B product page for promotional gifts",
"category": "Website",
"author": "SelectAd",
"depends": [
   'website_sale',
   'sale_management'
],
"data": [
    "views/product_page.xml",
    'views/bestsellers_page.xml',
    'views/shop_category_hero.xml',
    #"views/product_components.xml",
    'data/sequence.xml',
    #'security/ir.model.access.csv',
],
"assets": {
    "web.assets_frontend": [
        "gift_product_configurator/static/src/scss/product_page.scss",
        "gift_product_configurator/static/src/scss/bestsellers.scss",
        #"gift_product_configurator/static/src/scss/quote_drawer.scss",
        "gift_product_configurator/static/src/scss/shop_hero.scss",
        "gift_product_configurator/static/src/js/configurator.js",
        "gift_product_configurator/static/src/js/quote_drawer.js"
    ],
},
 'installable': True,
}
