# inspect the models to create a script that crates a key we can use to upload the data
from django.apps import apps

from data_distro.download_model_dictonaries import (
    table_mappings,
    file_to_table_name_mapping,
)


def make_table_structure():
    # From a given table, look at the column name and know where to load the data
    sample_data_structure = {
        "table file name": {
            "column_name": ["model_name", "django_field_name"],
            "column_name2": ["model_name", "django_field_name2"],
        }
    }

    no_help = []
    blank_help = []

    # preload tables into a dict
    upload_mapping = {}
    for table_title in table_mappings.keys():
        upload_mapping[table_title] = {}
        table_file = table_mappings[table_title]


    distro_classes = apps.all_models["data_distro"]
    # this should be enough to make a key
    for model in distro_classes:
        mod_class = distro_classes[model]
        mod_name = mod_class.__name__
        fields = mod_class._meta.get_fields()
        for field in fields:
            f_name = field.name
            try:
                help_text = field.help_text
            except:
                # relational fields won't have this, we can't load them directly anyway
                no_help.append([f_name, model])
            if "help_text" in locals() and help_text != "":
                if help_text != "":
                    source = help_text.split("Census mapping: ", 1)[1]
                    table_doc_name = source.split(", ", 1)[0]
                    column_name = source.split(", ", 1)[1]
                    table_file_name = file_to_table_name_mapping[
                        table_doc_name.upper().replace(" ", "")
                    ]
                    upload_mapping[table_file_name][column_name] = [mod_name, f_name]
                else:
                    blank_help.append([f_name, model])

    if len(blank_help) > 0:
        print("~ WARNING Check fields: {0} ~".format(blank_help))

    # this should relational fields
    print("Fields with no help: {0}".format(no_help))

    return(upload_mapping)


# last run's results
upload_mapping = {
    "gen": {
        "AUDITEECERTIFYNAME": ["General", "auditee_certify_name"],
        "AUDITEECERTIFYTITLE": ["General", "auditee_certify_title"],
        "AUDITEECONTACT": ["General", "auditee_contact"],
        "AUDITEEEMAIL": ["General", "auditee_email"],
        "AUDITEEFAX": ["General", "auditee_fax"],
        "AUDITEENAME": ["General", "auditee_name"],
        "AUDITEENAMETITLE": ["General", "auditee_name_title"],
        "AUDITEEPHONE": ["General", "auditee_phone"],
        "AUDITEETITLE": ["General", "auditee_title"],
        "STREET1": ["General", "street1"],
        "STREET2": ["General", "street2"],
        "CITY": ["General", "city"],
        "STATE": ["General", "state"],
        "ZIPCODE": ["General", "zip_code"],
        "COGAGENCY": ["General", "cognizant_agency"],
        "DUNS": ["General", "duns"],
        "UEI": ["General", "uei"],
        "MULTIPLEDUNS": ["General", "multiple_duns"],
        "MULTIPLEUEIS": ["General", "multiple_ueis"],
        "CPACITY": ["General", "cpa_city"],
        "CPACONTACT": ["General", "cpa_contact"],
        "CPACOUNTRY": ["General", "cpa_country"],
        "CPADATESIGNED": ["General", "cpa_date_signed"],
        "CPAEMAIL": ["General", "cpa_email"],
        "CPAFAX": ["General", "cpa_fax"],
        "CPAFIRMNAME": ["General", "cpa_firm_name"],
        "CPAFOREIGN": ["General", "cpa_foreign"],
        "CPAPHONE": ["General", "cpa_phone"],
        "CPASTATE": ["General", "cpa_state"],
        "CPASTREET1": ["General", "cpa_street1"],
        "CPASTREET2": ["General", "cpa_street2"],
        "CPATITLE": ["General", "cpa_title"],
        "CPAZIPCODE": ["General", "cpa_zip_code"],
        "AUDITOR_EIN": ["General", "auditor_ein"],
        "EIN": ["General", "ein"],
        "EINSUBCODE": ["General", "ein_subcode"],
        "MULTIPLEEINS": ["General", "multiple_eins"],
        "MULTIPLE_CPAS": ["General", "multiple_cpas"],
        "AUDITEEDATESIGNED": ["General", "auditee_date_signed"],
        "AUDITTYPE": ["General", "audit_type"],
        "AUDITYEAR": ["General", "audit_year"],
        "COMPLETED_ON": ["General", "completed_on"],
        "COMPONENT DATE RECEIVED": ["General", "component_date_received"],
        "REPORTABLECONDITION/SIGNIFICANTDEFICIENCY": [
            "General",
            "condition_or_deficiency",
        ],
        "REPORTABLECONDITION/SIGNIFICANTDEFICIENCY_MP": [
            "General",
            "condition_or_deficiency_major_program",
        ],
        "CYFINDINGS": ["General", "current_or_former_findings"],
        "DBKEY": ["General", "dbkey"],
        "DOLLARTHRESHOLD": ["General", "dollar_threshold"],
        "DUP_REPORTS": ["General", "dup_reports"],
        "ENTITY_TYPE": ["General", "entity_type"],
        "FAC ACCEPTED DATE": ["General", "fac_accepted_date"],
        "FORM DATE RECEIVED": ["General", "form_date_received"],
        "FYENDDATE": ["General", "fy_end_date"],
        "FYSTARTDATE": ["General", "fy_start_date"],
        "GOINGCONCERN": ["General", "going_concern"],
        "INITIAL DATE RECEIVED": ["General", "initial_date_received"],
        "LOWRISK": ["General", "low_risk"],
        "MATERIALNONCOMPLIANCE": ["General", "material_noncompliance"],
        "MATERIALWEAKNESS": ["General", "material_weakness"],
        "MATERIALWEAKNESS_MP": ["General", "material_weakness_major_program"],
        "NUMBERMONTHS": ["General", "number_months"],
        "OVERSIGHTAGENCY": ["General", "oversight_agency"],
        "PERIODCOVERED": ["General", "period_covered"],
        "PREVIOUS_COMPLETED_ON": ["General", "previous_completed_on"],
        "PYSCHEDULE": ["General", "prior_year_schedule"],
        "QCOSTS": ["General", "questioned_costs"],
        "REPORTREQUIRED": ["General", "report_required"],
        "SP_FRAMEWORK": ["General", "sp_framework"],
        "SP_FRAMEWORK_REQUIRED": ["General", "sp_framework_required"],
        "TOTFEDEXPEND": ["General", "total_fed_expenditures"],
        "TYPEOFENTITY": ["General", "type_of_entity"],
        "TYPEREPORT_FS": ["General", "type_report_financial_statements"],
        "TYPEREPORT_MP": ["General", "type_report_major_program"],
        "TYPEREPORT_SP_FRAMEWORK": ["General", "type_report_special_purpose_framework"],
    },
    "cfda": {
        "R&D": ["CfdaInfo", "research_and_development"],
        "LOANS": ["CfdaInfo", "loans"],
        "ARRA": ["CfdaInfo", "arra"],
        "DIRECT": ["CfdaInfo", "direct"],
        "PASSTHROUGHAWARD": ["CfdaInfo", "passthrough_award"],
        "MAJORPROGRAM": ["CfdaInfo", "major_program"],
        "FINDINGREFNUMS": ["CfdaInfo", "finding_ref_nums"],
        "AMOUNT": ["CfdaInfo", "amount"],
        "PROGRAMTOTAL": ["CfdaInfo", "program_total"],
        "CLUSTERTOTAL": ["CfdaInfo", "cluster_total"],
        "PASSTHROUGHAMOUNT": ["CfdaInfo", "passthrough_amount"],
        "LOANBALANCE": ["CfdaInfo", "loan_balance"],
        "FEDERALPROGRAMNAME": ["CfdaInfo", "federal_program_name"],
        "CFDAPROGRAMNAME": ["CfdaInfo", "cfda_program_name"],
        "AWARDIDENTIFICATION": ["CfdaInfo", "award_identification"],
        "CFDA": ["CfdaInfo", "cfda"],
        "CLUSTERNAME": ["CfdaInfo", "cluster_name"],
        "STATECLUSTERNAME": ["CfdaInfo", "state_cluster_name"],
        "OTHERCLUSTERNAME": ["CfdaInfo", "other_cluster_name"],
        "TYPEREQUIREMENT": ["CfdaInfo", "type_requirement"],
        "TYPEREPORT_MP": ["CfdaInfo", "type_report_major_program"],
        "FINDINGSCOUNT": ["CfdaInfo", "findings_count"],
        "ELECAUDITSID": ["CfdaInfo", "elec_audits_id"],
        "DBKEY": ["CfdaInfo", "dbkey"],
        "AUDITYEAR": ["CfdaInfo", "audit_year"],
    },
    "findings": {
        "MODIFIEDOPINION": ["Findings", "modified_opinion"],
        "OTHERNONCOMPLIANCE": ["Findings", "other_non_compliance"],
        "MATERIALWEAKNESS": ["Findings", "material_weakness"],
        "SIGNIFICANTDEFICIENCY": ["Findings", "significant_deficiency"],
        "OTHERFINDINGS": ["Findings", "other_findings"],
        "QCOSTS": ["Findings", "questioned_costs"],
        "REPEATFINDING": ["Findings", "repeat_finding"],
        "FINDINGREFNUMS": ["Findings", "finding_ref_nums"],
        "PRIORFINDINGREFNUMS": ["Findings", "prior_finding_ref_nums"],
        "TYPEREQUIREMENT": ["Findings", "type_requirement"],
        "ELECAUDITSID": ["Findings", "elec_audits_id"],
        "ELECAUDITFINDINGSID": ["Findings", "elec_audit_findings_id"],
        "AUDITYEAR": ["Findings", "audit_year"],
        "DBKEY": ["Findings", "dbkey"],
    },
    "findingstext_formatted": {
        "CHARTSTABLES": ["FindingsText", "charts_tables"],
        "FINDINGREFNUMS": ["FindingsText", "finding_ref_nums"],
        "SEQ_NUMBER": ["FindingsText", "seq_number"],
        "TEXT": ["FindingsText", "text"],
        "DBKEY": ["FindingsText", "dbkey"],
        "AUDITYEAR": ["FindingsText", "audit_year"],
    },
    "captext_formatted": {
        "CHARTSTABLES": ["CapText", "charts_tables"],
        "FINDINGREFNUMS": ["CapText", "finding_ref_nums"],
        "SEQ_NUMBER": ["CapText", "seq_number"],
        "TEXT": ["CapText", "text"],
        "DBKEY": ["CapText", "dbkey"],
        "AUDITYEAR": ["CapText", "audit_year"],
    },
    "notes": {
        "TYPE_ID": ["Notes", "type_id"],
        "ID": ["Notes", "fac_id"],
        "REPORTID": ["Notes", "report_id"],
        "VERSION": ["Notes", "version"],
        "SEQ_NUMBER": ["Notes", "seq_number"],
        "NOTE_INDEX": ["Notes", "note_index"],
        "CONTENT": ["Notes", "content"],
        "TITLE": ["Notes", "title"],
        "DBKEY": ["Notes", "dbkey"],
        "AUDITYEAR": ["Notes", "audit_year"],
    },
    "cpas": {
        "CPAPHONE": ["MultipleCpasInfo", "cpa_phone"],
        "CPAFAX": ["MultipleCpasInfo", "cpa_fax"],
        "CPASTATE": ["MultipleCpasInfo", "cpa_state"],
        "CPACITY": ["MultipleCpasInfo", "cpa_city"],
        "CPATITLE": ["MultipleCpasInfo", "cpa_title"],
        "CPASTREET1": ["MultipleCpasInfo", "cpa_street1"],
        "CPAZIPCODE": ["MultipleCpasInfo", "cpa_zip_code"],
        "CPACONTACT": ["MultipleCpasInfo", "cpa_contact"],
        "CPAEMAIL": ["MultipleCpasInfo", "cpa_email"],
        "CPAFIRMNAME": ["MultipleCpasInfo", "cpa_firm_name"],
        "CPAEIN": ["MultipleCpasInfo", "cpa_ein"],
        "DBKEY": ["MultipleCpasInfo", "dbkey"],
        "AUDITYEAR": ["MultipleCpasInfo", "audit_year"],
        "SEQNUM": ["Revisions", "general"],
    },
    "revisions": {
        "FINDINGS": ["Revisions", "findings"],
        "ELECRPTREVISIONID": ["Revisions", "elec_report_revision_id"],
        "FEDERALAWARDS": ["Revisions", "federal_awards"],
        "GENINFO_EXPLAIN": ["Revisions", "general_info_explain"],
        "FEDERALAWARDS_EXPLAIN": ["Revisions", "federal_awards_explain"],
        "NOTESTOSEFA_EXPLAIN": ["Revisions", "notes_to_sefa_explain"],
        "AUDITINFO_EXPLAIN": ["Revisions", "auditinfo_explain"],
        "FINDINGS_EXPLAIN": ["Revisions", "findings_explain"],
        "FINDINGSTEXT_EXPLAIN": ["Revisions", "findings_text_explain"],
        "CAP_EXPLAIN": ["Revisions", "cap_explain"],
        "OTHER_EXPLAIN": ["Revisions", "other_explain"],
        "AUDITINFO": ["Revisions", "audit_info"],
        "NOTESTOSEFA": ["Revisions", "notes_to_sefa"],
        "FINDINGSTEXT": ["Revisions", "findings_text"],
        "CAP": ["Revisions", "cap"],
        "OTHER": ["Revisions", "other"],
        "GENINFO": ["Revisions", "general_info"],
        "AUDITYEAR": ["Revisions", "audit_year"],
        "DBKEY": ["Revisions", "dbkey"],
    },
    "ueis": {
        "UEI": ["UeiInfo", "uei"],
        "UEISEQNUM": ["UeiInfo", "uei_seq_num"],
        "DBKEY": ["UeiInfo", "dbkey"],
        "AUDITYEAR": ["Agencies", "general"],
    },
    "agency": {
        "AGENCYCFDA": ["Agencies", "agency_cfda"],
        "EIN": ["Agencies", "ein"],
        "DBKEY": ["Agencies", "dbkey"],
        "AUDITYEAR": ["Agencies", "audit_year"],
    },
    "passthrough": {
        "PASSTHROUGHNAME": ["Passthrough", "passthrough_name"],
        "PASSTHROUGHID": ["Passthrough", "passthrough_id"],
        "ELECAUDITSID": ["Passthrough", "elec_audits_id"],
        "AUDITYEAR": ["Passthrough", "audit_year"],
        "DBKEY": ["Passthrough", "dbkey"],
    },
    "eins": {
        "EIN": ["EinInfo", "ein"],
        "EINSEQNUM": ["EinInfo", "ein_seq_num"],
        "DBKEY": ["EinInfo", "dbkey"],
        "AUDITYEAR": ["EinInfo", "audit_year"],
    },
    "duns": {
        "DUNS": ["DunsInfo", "duns"],
        "DUNSEQNUM": ["DunsInfo", "duns_seq_num"],
        "DBKEY": ["DunsInfo", "dbkey"],
        "AUDITYEAR": ["DunsInfo", "audit_year"],
    },
}
