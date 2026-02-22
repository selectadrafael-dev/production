{
"name": "Gift Product Configurator",
"version": "18.01.08",
"summary": "Advanced B2B product page for promotional gifts",
"category": "Website",
"author": "SelectAd",
"depends": [
    "website", 
    "product", 
    "sale",
    "website_sale",
    "sale_management",
],
"data": [
    "views/product_page.xml",
    "views/product_components.xml",
],
"assets": {
    "web.assets_frontend": [
    "gift_product_configurator/static/src/js/configurator.js",
    "gift_product_configurator/static/src/scss/product_page.scss",
    ],
},
 'installable': True,
}
