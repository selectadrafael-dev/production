{
    "name": "Gifting Theme",
    "version": "21.0.1.0.0",
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
        #"views/assets.xml",
        'views/layout.xml',
        #'views/theme.xml',
        "views/header.xml",
        "views/hero.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "theme_gifting/static/src/css/header.css",
            "theme_gifting/static/src/css/hero.css",
        ],
    },
    "theme": True,
    "installable": True,
}
