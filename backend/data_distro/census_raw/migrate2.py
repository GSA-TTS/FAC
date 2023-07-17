import pandas as pd
import numpy as np

import pandas as pds

from sqlalchemy import create_engine

from local_models.cfac import (
    ELECFINDINGSTEXT as CFAC_FT,
    ELECAUDITHEADER as CFAC_GEN
)

from local_models.gfac import (
    general as GFAC_GEN,
    findingtext as GFAC_FT
)

gen_mapping = {'agencycfda' : None, 
               'auditeecertifyname': 'auditee_certify_name',
                'auditeecertifytitle': 'auditee_certify_title', 
                'auditeecontact': 'auditee_contact_name', 
                'auditeedatesigned': 'auditee_certified_date', 
                'auditeeemail': 'auditee_email', 
                'auditeefax': 'hist_auditee_fax', 
                'auditeename': 'auditee_name', 
                'auditeenametitle': None, 
                'auditeephone': 'auditee_phone', 
                'auditeetitle': 'auditee_contact_title', 
                'auditor_ein': 'auditor_ein', 
                'audittype': 'audit_type', 
                'audityear': 'audit_year', 
                'city': 'auditee_city', 
                'cog_agency': 'cognizant_agency', 
                'cog_over': None, 
                'cogagency': None, 
                'copies': None, 
                'cpacity': 'auditor_city', 
                'cpacontact': 'auditor_contact_name', 
                'cpacountry': 'auditor_country', 
                'cpadatesigned': 'auditor_certified_date', 
                'cpaemail': 'auditor_email', 
                'cpafax': 'hist_auditor_fax', 
                'cpafirmname': 'auditor_firm_name', 
                'cpaforeign': 'auditor_foreign_addr', 
                'cpanametitle': None, 
                'cpaphone': 'auditor_phone', 
                'cpastate': 'auditor_state', 
                'cpastreet1': 'auditor_address_line_1', 
                'cpastreet2': 'hist_auditor_address_line_2', 
                'cpatitle': 'auditor_contact_title', 
                'cpazipcode': 'auditor_zip',
                'cyfindings': 'current_or_former_findings', 
                'datefinished': 'date_published', 
                'datefirewall': None, 
                'datereceived': 'date_received', 
                'datereceivedother': 'form_date_received', 
                'datetoed': None, 
                'dbkey': 'dbkey', 
                'dollarthreshold': 'dollar_threshold', 
                'duns': None, 
                'dup_reports': None, 
                'ein': 'auditee_ein', 
                'einsubcode': 'ein_subcode', 
                'elecauditheaderid': None, 
                'entity_type': 'entity_type', 
                'facaccepteddate': 'fac_accepted_date', 
                'findingrefnum': None, 
                'fyenddate': 'fy_end_date', 
                'fystartdate': 'fy_start_date', 
                'goingconcern': None, 
                'id': None, 
                'image': None, 
                'initialdate': 'create_date', 
                'lowrisk': 'is_low_risk', 
                'materialnoncompliance': 'is_material_noncompliance', 
                'materialweakness': 'is_material_weakness', 
                'materialweakness_mp': None, 
                'multiple_cpas': None, 
                'multipleduns': None,  
                'multipleeins': None, 
                'multipleueis': None, 
                'numbermonths': None, 
                'opeid': None, 
                'oversightagency': 'oversight_agency', 
                'periodcovered': 'audit_period_covered', 
                'previousdatefirewall': None, 
                'pyschedule': 'prior_year_schedule', 
                'qcosts': 'questioned_costs', 
                'reportablecondition': None, 
                'reportablecondition_mp': None, 
                'reportrequired': None, 
                'sd_materialweakness': None, 
                'sd_materialweakness_mp': None, 
                'significantdeficiency': 'is_significant_deficiency', 
                'significantdeficiency_mp': None, 
                'sp_framework': 'special_framework', 
                'sp_framework_required': None, 
                'state': 'auditee_state', 
                'street1': 'auditee_address_line_1', 
                'street2': 'hist_auditee_address_line_2', 
                'suppression_code': 'suppression_code', 
                'totfedexpend': 'total_fed_expenditures', 
                'typeaudit_code': 'type_audit_code', 
                'typefinding': None, 
                'typefunding': None, 
                'typeofentity': None, 
                'typereport_fs': 'type_report_financial_statements', 
                'typereport_mp': 'type_report_major_program', 
                'typereport_sp_framework': 'type_report_special_purpose_framework', 
                'uei': 'auditee_uei', 
                'zipcode': 'auditee_zip'
                }


REPORT_ID = 0
def next_report_id(year, d):
    global REPORT_ID
    REPORT_ID += 1
    month = "UNKNOWN"
    if d:
        month = d.strftime('%B')
    return f"{year}-{month}-{REPORT_ID}"

def main():

    aE   = create_engine('postgresql+psycopg2://postgres:@localhost:5432', pool_recycle=3600)
    conn = aE.connect()

    # GFAC_GEN.database.create_tables([GFAC_GEN.DisseminationGeneral])
    
    # print(CFAC_GEN.Elecauditheader._meta.sorted_field_names)
    df = pd.read_sql_query('select * from "ELECAUDITHEADER" where (audityear=\'2021\' and entity_type=\'State\')', 
                    conn
                    )
    to_map = {}
    to_remove = {}
    for k, v in gen_mapping.items():
        if v:
            to_map[k] = v
        else:
            to_remove[k] = v

    df = df.drop(columns=list(to_remove.keys()))
    df = df.rename(columns=to_map)

    df['report_id'] = np.NaN
    for ndx in range(len(df)):
        df.at[ndx, 'report_id'] = next_report_id(df.at[ndx, 'audit_year'],
                                                 df.at[ndx, 'date_published']
        )

    df['data_source'] = "CFAC"
    # Downcast from float
    df = df.astype({'dbkey': int})
    df = df.astype({'dbkey': str})
    
    # I lost an hour to this: pass the engine, not the connection
    # object. Why? I don't know.
    # https://stackoverflow.com/questions/48307008/pandas-to-sql-doesnt-insert-any-data-in-my-table#:~:text=passing%20sqlalchemy%20connection%20object%20instead%20of%20engine%20object%20to%20the%20con%20parameter
    df.to_sql('dissemination_general', 
              aE, 
              if_exists='replace', 
              index=False, 
              chunksize=1000,
              schema='public')

    print(df[0:10])

main()

# pd.read_sql()