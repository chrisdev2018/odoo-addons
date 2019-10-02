# -*- encoding: utf-8 -*-
# Python source code encoding : https://www.python.org/dev/peps/pep-0263/
{
    # Theme information
    'name': "Module Debranding",
    'category': 'Theme',
    'version': '1.0',

    # Dependencies
    'depends': [
        'web',
        'web_debranding',
        'web_debranding',
        'web_debranding_support'
    ],
    'external_dependencies': {},

    # Views templates, pages, menus, options and snippets
    'data': ['views/web_views_webclient_templates.xml'],

    # Qweb templates
    'qweb': [],

    # Your information
    'author': 'Christian FOMEKONG',
    'website': 'https://github.com/chrisdev2018',
    'license': 'AGPL-3',

    # Technical options
    'demo': [],
    'test': [],
    'installable': True,
    # 'auto_install':False,
    # 'active':True,
}
