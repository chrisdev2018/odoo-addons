# -*-coding: utf-8 -*-
{
    'name': "Corpecca Paie ",

    'summary': "Module de personnalisation de la paie pour le Cameroun",

    'description': """""",

    'author': "Corpecca",

    'version': '0.0.1',

    'depends': ['base', 'hr_payroll', 'report_xls', 'hr_payroll_cancel'],

    'data': [

        # data
        # "data/hr.salary.rule.category.csv",
        # "data/hr.salary.rule.csv",
        "data/menus.xml",

        # wizards
        "wizards/wizard_statistiques_views.xml",
        "wizards/wizard_declarations_views.xml",
        "wizards/securite_cnps_wizard_views.xml",
        "wizards/dipes_mensuel_wizard_views.xml",
        "wizards/virement_bancaire_wizard_views.xml",
        "wizards/dipe_nominal_wizard_views.xml",
        "wizards/etat_cotisation_wizard_views.xml",

        # reports
        "reports/paper_format.xml",
        "reports/bulletin_paie.xml",
        "reports/hr_masse_salaire_view.xml",
        "reports/statistiques_views.xml",
        "reports/dipes_mensuel_xls_views.xml",
        "reports/etat_cotisation_report_views.xml",
        "reports/journal_paie_report.xml",

        # security
        "security/ir.model.access.csv",

        # views
        "views/menu.xml",
        "views/hr_contract_views.xml",
        "views/categorie_salariale_views.xml",
        "views/echelon_salariale_views.xml",
        "views/grille_salaire_views.xml",
        "views/hr_contract_type_views.xml",
        "views/banque_view.xml",
        "views/employee_view.xml",
        "views/prime_ind_views.xml",
        "views/hr_department_views.xml",
        "views/res_company_views.xml",
        "views/hr_payslip_views.xml",
        "views/hr_payslip_run_views.xml",
        "views/hr_config_settings_views.xml",
        "views/hr_salary_rule_views.xml",
        "views/centre_rh_views.xml",

    ],

    'website': "www.corpecca.africa",

}
