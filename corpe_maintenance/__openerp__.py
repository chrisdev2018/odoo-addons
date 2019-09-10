# -*-coding: utf-8 -*-
{
    'name': "Corpecca Maintenance ",

    'summary': "Module de gestion de la maintennace",

    'description': """
                      Ce module permettra entre autre de gerer les demandes d'intervention, les equipements,
                      les ordres de travail, les fiches d'activite etc.  """,

    'author': "Corpecca",

    'version': '0.0.1',

    'depends': ['base',
                'report_xls',
                'stock',
                'hr',
                'project',
                'product'
                ],

    'data': [
        "data/sequences.xml",
        # data

        # wizards

        # reports

        # security
        "security/groups.xml",
        "security/ir.model.access.csv",
        # views
        "views/type_panne_views.xml",
        "views/centre_maintenance_views.xml",
        "views/bon_travail_views.xml",
        "views/demande_intervention_views.xml",
        "views/ligne_production_views.xml",
        "views/equipement_views.xml",
        "views/fiche_activite_views.xml",
        "views/dashbord_views.xml",
        "views/menus.xml",
        "views/product_template_views.xml",
    ],

    'website': "www.corpecca.africa",

}
