{
    "name": "Gifting Theme",
    "description": "Custom theme for corporate gifting platform",
    "version": "1.0",
    "author": "SelectAd",
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
        "views/assets.xml",
        "views/header.xml",
        "views/hero.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "theme_gifting/static/src/css/hero.css",
        ],
    },
    "theme": True,
    "installable": True,
    "application": False,
}
