import typing
import time
from peewee import *
from playhouse.shortcuts import model_to_dict, dict_to_model

from dateutil import parser
import datetime

import uuid

from local_models.cfac import (
    ELECFINDINGSTEXT as CFAC_FT,
    ELECAUDITHEADER as CFAC_GEN
)

from local_models.gfac import (
    general as GFAC_GEN,
    findingtext as GFAC_FT
)

CHUNKS = 100

    # id = BigAutoField()
    # report_id = CharField()
    # finding_ref_number = CharField(null=True)
    # charts_tables = BooleanField(null=True)
    # finding_text = TextField(null=True)

def migrate_eft(gens):
    for g in gens:
        efts = (CFAC_FT.Elecfindingstext()
                .select()
                .where(CFAC_FT.Elecfindingstext.dbkey == g.dbkey,
                       CFAC_FT.Elecfindingstext.audityear == g.audityear))
        efts_subls = [efts[i:i+CHUNKS] for i in range(0, len(efts), CHUNKS)]  
        print(f"Processing {len(efts_subls)} sublists of FTs")
        for efts in efts_subls:
            with GFAC_FT.database.transaction() as txn:
                for e in efts:
                    ge = GFAC_FT.DisseminationFindingtext(
                        id = e.id,
                        report_id = uuid.uuid4(),
                        finding_ref_number = e.findingrefnums,
                        charts_tables = e.chartstables,
                        finding_text = e.text
                        )
                    ge.save()
                txn.commit()

ID = 0
def next_id():
    global ID
    ID += 1
    return ID

REPORT_ID = 0
def next_report_id(year, d):
    global REPORT_ID
    REPORT_ID += 1
    month = "UNKNOWN"
    if d:
        month = d.strftime('%B')

    return f"{year}-{month}-{REPORT_ID}"

def migrate_general_entries(all_gens, is_public):
    print(f"Processing {len(all_gens)} FTs")
    g : CFAC_GEN.Elecauditheader
    for g in all_gens:
            dg = None
            try:
                dg = GFAC_GEN.DisseminationGeneral(
                            id = next_id(),    
                            report_id = next_report_id(g.audityear, g.fyenddate),
                            audit_period_covered = g.periodcovered,
                            audit_type = g.audittype,
                            audit_year = g.audityear,
                            auditee_addl_duns_list = None,
                            auditee_addl_ein_list = None,
                            auditee_addl_uei_list = None,
                            auditee_address_line_1 = g.street1,
                            auditee_certified_date = g.auditeedatesigned,
                            auditee_certify_name = g.auditeecertifyname,
                            auditee_certify_title = g.auditeecertifytitle,
                            auditee_city = g.city,
                            auditee_contact_name = g.auditeecontact,
                            auditee_contact_title = g.auditeetitle,
                            auditee_duns = g.duns,
                            auditee_ein = g.ein,
                            auditee_email = g.auditeeemail,
                            auditee_name = g.auditeename,
                            auditee_phone = g.auditeephone,
                            auditee_state = g.state,
                            auditee_uei = g.uei,
                            auditee_zip = g.zipcode,
                            auditor_address_line_1 = g.cpastreet1,
                            auditor_certified_date = g.cpadatesigned,
                            auditor_city = g.cpacity,
                            auditor_contact_name = g.cpacontact,
                            auditor_contact_title = g.cpatitle,
                            auditor_country = g.cpacountry,
                            auditor_ein = g.auditor_ein,
                            auditor_email = g.cpaemail,
                            auditor_firm_name = g.cpafirmname,
                            auditor_foreign_addr = g.cpaforeign,
                            auditor_phone = g.cpaphone,
                            auditor_state = g.cpastate,
                            auditor_zip = g.cpazipcode,
                            cfac_report_id = g.id,
                            cfac_version = None,
                            # FIXME: Which is it?
                            cognizant_agency = (g.cog_agency or g.cogagency),
                            # FIXME: ?
                            condition_or_deficiency_major_program = g.significantdeficiency_mp,
                            # FIXME: ? 
                            create_date = None,
                            # FIXME: ?
                            current_or_former_findings = g.findingrefnum,
                            data_source = None,
                            date_published = g.datefinished,
                            date_received = g.datereceived,
                            dbkey = g.dbkey,
                            dollar_threshold = g.dollarthreshold,
                            ein_subcode = g.einsubcode,
                            entity_type = g.entity_type,
                            fac_accepted_date = g.facaccepteddate,
                            # FIXME
                            form_date_received = g.datereceived,
                            fy_end_date = g.fyenddate,
                            fy_start_date = g.fystartdate,
                            hist_auditee_address_line_2 = None,
                            hist_auditee_fax = None,
                            hist_auditor_address_line_2 = None,
                            hist_auditor_fax = None,
                            hist_completed_date = None,
                            hist_component_date_received = None,
                            hist_previous_completed_on = None,
                            hist_previous_date_published = None,
                            hist_reportable_condition = None,
                            hist_type_of_entity = None,
                            initial_date_received = None,
                            is_duplicate_reports = g.dup_reports,
                            is_going_concern = g.goingconcern,
                            is_low_risk = g.lowrisk,
                            is_material_noncompliance = g.materialnoncompliance,
                            is_material_weakness = g.materialweakness,
                            is_public = is_public,
                            is_significant_deficiency = g.significantdeficiency,
                            is_special_framework_required = g.sp_framework_required,
                            material_weakness = g.materialweakness,
                            material_weakness_major_program = g.materialweakness_mp,
                            # FIXME: ? 
                            modified_date = None,
                            multiple_auditors = g.multiple_cpas,
                            multiple_duns = g.multipleduns,
                            multiple_ein = g.multipleeins,
                            multiple_uei = g.multipleueis,
                            number_months = g.numbermonths,
                            oversight_agency = g.oversightagency,
                            # FIXME: TBD
                            pdf_url = None,
                            # FIXME: ?
                            prior_year_schedule = None,
                            questioned_costs = g.qcosts,
                            report_required = g.reportrequired,
                            special_framework = g.sp_framework,
                            # FIXME: This is either IT or AG. 
                            # What do those mean?
                            suppression_code = g.suppression_code,
                            total_fed_expenditures = g.totfedexpend,
                            type_audit_code = g.typeaudit_code,
                            type_report_financial_statements = g.typereport_fs,
                            type_report_major_program = g.typereport_mp,
                            type_report_special_purpose_framework = g.typereport_sp_framework,
                    )
            except Exception as e:
                    print(f"Could not create storage object.")

            if dg:
                try:
                    with GFAC_FT.database.atomic():
                        dg.save()
                        GFAC_FT.database.commit()
                        print(f"{dg.report_id} saved.")
                except Exception as e:
                    GFAC_FT.database.rollback()
                    print(f"Did not save DG model {dg.report_id}")
                    print(e)
                

def initial_general_entries(year='2021'):
    gens = (CFAC_GEN.Elecauditheader()
            .select()
            # WARNING: We only want public data.
            # State audits should always be public, as they are not 
            # tribal entities.
            .where(CFAC_GEN.Elecauditheader.audityear == year,
                   CFAC_GEN.Elecauditheader.entity_type == 'State')
            )
    return gens

gens = initial_general_entries()
# First, migrate all the general entries.
# This can then be used to drive the migration
# of other tables. This is necessary, because of linking.
migrate_general_entries(gens, is_public=True)
