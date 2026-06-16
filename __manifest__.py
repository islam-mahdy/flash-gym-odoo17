{
    'name': "Flash Gym",
    'summary': "",
    'description': """
    """,
    'version': '0.1',
    'author': "Islam Mahdy",
    'website': "https://www.flashGYM.com",

    'category': 'health',

    'depends': ['base', 'mail'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron.xml',
        'views/member_views.xml',
        'views/subscription_plan_views.xml',
        'views/coach_views.xml',
        'views/membership_views.xml',
        'views/class_views.xml',
        'views/booking_views.xml',
        'views/checkin_views.xml',
        'views/payment_views.xml',
        'views/menu.xml',
        'wizards/payment_wizard_views.xml',
        'reports/payment_reports.xml',
        'data/demo_specialization.xml',
        'data/weekday_data.xml',
    ],

    # 'demo': [
    #     'data/demo.xml',
    # ],

    "application": True,
    "installable": True,
    "auto_install": False,
}

