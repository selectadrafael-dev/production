{
    "name": "Gifting Theme",
    "version": "18.0.1.0.0",
    "category": "Theme/Corporate",
    "depends": [
        "website", 
        "product", 
        "sale",
        "website_sale",
        "sale_management",
        "payment",
        "website_sale_wishlist", 
    ],
    "data": [
        'views/layout.xml',
        #'views/theme.xml',
        "views/header.xml",
        "views/hero.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "theme_gifting/static/src/css/header.css",
            "theme_gifting/static/src/css/hero.css",
            "theme_gifting/static/src/css/product.css",
            "theme_gifting/static/src/js/cart_count.js",
            "theme_gifting/static/src/js/header.js",
        ],
    },
    "theme": True,
    "installable": True,
}
