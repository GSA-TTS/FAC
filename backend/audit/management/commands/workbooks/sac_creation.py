"""Fixtures for SingleAuditChecklist.

We want to create a variety of SACs in different states of
completion.
"""
from datetime import date, timedelta
import logging
from pathlib import Path

from django.apps import apps
# from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
import random
import uuid

from audit.excel import (
    extract_federal_awards,
    extract_findings_uniform_guidance,
    extract_findings_text,
    extract_corrective_action_plan,
    extract_secondary_auditors,
    extract_notes_to_sefa,
    extract_additional_ueis,
)
import audit.validators

from audit.fixtures.excel import FORM_SECTIONS
# from users.models import User

logger = logging.getLogger(__name__)

from audit.management.commands.workbooks.excel_creation import dbkey_to_test_report_id
from audit.management.commands.census_models.ay22 import CensusGen22 as Gen

from audit.management.commands.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusCfda22 as Cfda,
    CensusFindings22 as Finding
)

def get_field_by_section(sac, section):
    if section == FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED:
        return sac.federal_awards
    elif section == FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE:
        return sac.findings_uniform_guidance
    elif section == FORM_SECTIONS.FINDINGS_TEXT:
        return sac.findings_text
    elif section == FORM_SECTIONS.CORRECTIVE_ACTION_PLAN:
        return sac.corrective_action_plan
    elif section == FORM_SECTIONS.SECONDARY_AUDITORS:
        return sac.secondary_auditors
    elif section == FORM_SECTIONS.NOTES_TO_SEFA:
        return sac.notes_to_sefa
    elif section == FORM_SECTIONS.ADDITIONAL_UEIS:
        return sac.additional_ueis


extract_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: extract_federal_awards,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: extract_findings_uniform_guidance,
    FORM_SECTIONS.FINDINGS_TEXT: extract_findings_text,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: extract_corrective_action_plan,
    FORM_SECTIONS.SECONDARY_AUDITORS: extract_secondary_auditors,
    FORM_SECTIONS.NOTES_TO_SEFA: extract_notes_to_sefa,
    FORM_SECTIONS.ADDITIONAL_UEIS: extract_additional_ueis,
}

validator_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: audit.validators.validate_federal_award_json,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: audit.validators.validate_findings_uniform_guidance_json,
    FORM_SECTIONS.FINDINGS_TEXT: audit.validators.validate_findings_text_json,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: audit.validators.validate_corrective_action_plan_json,
    FORM_SECTIONS.SECONDARY_AUDITORS: audit.validators.validate_secondary_auditors_json,
    FORM_SECTIONS.NOTES_TO_SEFA: audit.validators.validate_notes_to_sefa_json,
    FORM_SECTIONS.ADDITIONAL_UEIS: audit.validators.validate_additional_ueis_json,
    "PDF": audit.validators.validate_single_audit_report_file,
}

def _census_date_to_datetime(cd):
    lookup = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5,
        "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, 
        "NOV": 11, "DEC": 12
    }
    year = int(cd.split("-")[2])
    month = lookup[cd.split("-")[1]]
    day = int(cd.split("-")[0])
    return date(year+2000, month, day)

def _period_covered(s):
    return {"A": "annual", "B": "biennial", "O": "other"}[s]

def _census_audit_type(s):
    return {"S": "single-audit"}[s]

def _fake_general_information(dbkey, auditee_name=None):
    """Create a fake general_information object."""
    # TODO: can we generate this object from the schema definition in
    # schemas/output/GeneralInformation.schema.json?
    gobj: Gen = Gen.select().where(Gen.dbkey==dbkey).first()
    auditee_fiscal_period_end = _census_date_to_datetime(gobj.fyenddate).strftime("%Y-%m-%d")
    auditee_fiscal_period_start = (_census_date_to_datetime(gobj.fyenddate) - timedelta(days=365)).strftime(
            "%Y-%m-%d"
        )
    general_information = {
        "auditee_fiscal_period_start": auditee_fiscal_period_start,
        "auditee_fiscal_period_end":  auditee_fiscal_period_end,
        "audit_period_covered": _period_covered(gobj.periodcovered),
        "audit_type": _census_audit_type(gobj.audittype),
        "auditee_address_line_1": gobj.street1,
        "auditee_city": gobj.city,
        "auditee_contact_name": gobj.auditeecontact,
        "auditee_contact_title": gobj.auditeetitle,
        "auditee_email": gobj.auditeeemail,
        "auditee_name": gobj.auditeename,
        "auditee_phone": gobj.auditeephone,
        # TODO: when we include territories in our valid states, remove this restriction
        "auditee_state": gobj.state,
        # TODO: this is GSA's UEI. We could do better at making random choices that
        # pass the schema's complex regex validation
        "auditee_uei": gobj.uei,
        "auditee_zip": gobj.zipcode,
        "auditor_address_line_1": gobj.cpastreet1,
        "auditor_city": gobj.cpacity,
        "auditor_contact_name": gobj.cpacontact,
        "auditor_contact_title": gobj.cpatitle,
        "auditor_country": gobj.cpacountry,
        "auditor_ein": gobj.auditor_ein,
        "auditor_ein_not_an_ssn_attestation": True,
        "auditor_email": gobj.cpaemail,
        "auditor_firm_name": gobj.cpafirmname,
        "auditor_phone": gobj.cpaphone,
        # TODO: when we include territories in our valid states, remove this restriction
        "auditor_state": gobj.cpastate,
        "auditor_zip": gobj.cpazipcode,
        "ein": gobj.ein,
        "ein_not_an_ssn_attestation": True,
        "is_usa_based": True,
        "met_spending_threshold": True,
        "multiple_eins_covered": True if gobj.multipleeins == "Y" else False,
        "multiple_ueis_covered": True if gobj.multipleueis == "Y" else False,
        # TODO: could improve this by randomly choosing from the enum of possible values
        "user_provided_organization_type": "unknown",
    }

    # verify that our created object validates against the schema
    audit.validators.validate_general_information_json(general_information)

    return general_information


# TODO: Pull this from actual information.
def _fake_audit_information(dbkey, auditee_name=None):
    gobj: Gen = Gen.select().where(Gen.dbkey==dbkey).first()
    cfdas = Cfda.select().where(Cfda.dbkey==dbkey)

    agencies = {}
    cfda: Cfda
    for cfda in cfdas:
        agencies[int((cfda.cfda).split(".")[0])] = 1

    findings = Finding.select().where(Finding.dbkey==dbkey)
    finding: Finding
    gaap_results = {}
    # THIS IS NOT A GOOD WAY TO DO THIS, BUT IT IS CLOSE.
    # IT IS FOR TEST DATA...
    for finding in findings:
        if finding.modifiedopinion == "Y":
            gaap_results["unmodified_opinion"] = 1
        if finding.materialweakness == "Y":
            gaap_results["adverse_opinion"] = 1
        if finding.significantdeficiency == "Y":
            gaap_results["disclaimer_of_opinion"] = 1
        

    audit_information = {
        "agencies": list(map(lambda i: str(i), agencies.keys())),
        "dollar_threshold": 750000,
        "gaap_results": list(gaap_results.keys()),
        "is_aicpa_audit_guide_included": True if gobj.reportablecondition == "Y" else False,
        "is_going_concern_included": True if gobj.goingconcern == "Y" else False,
        "is_internal_control_deficiency_disclosed": True if gobj.materialweakness == "Y" else False,
        "is_internal_control_material_weakness_disclosed": True if gobj.materialweakness_mp == "Y" else False,
        "is_low_risk_auditee": False,
        "is_material_noncompliance_disclosed": True if gobj.materialnoncompliance == "Y" else False,
    }

    audit.validators.validate_audit_information_json(audit_information)

    return audit_information

def _create_test_sac(user, auditee_name, dbkey):
    """Create a single example SAC."""
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")

    try:
        exists = SingleAuditChecklist.objects.get(report_id=dbkey_to_test_report_id(Gen, dbkey))
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()
        
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_fake_general_information(dbkey, auditee_name),
        audit_information=_fake_audit_information(dbkey, auditee_name),
    )
    # Set a TEST report id for this data
    sac.report_id = dbkey_to_test_report_id(Gen, dbkey)

    Access = apps.get_model("audit.Access")
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )
    # Why not give me all the access? This way, I can run the test all the way through!
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="certifying_auditor_contact",
    )
    sac.data_source = "TEST DATA"
    sac.save()

    logger.info("Created single audit checklist %s", sac)
    return sac

def _make_excel_file(filename, f_obj):
    content = f_obj.read()
    f_obj.seek(0)
    file = SimpleUploadedFile(filename, content, "application/vnd.ms-excel")
    return file


def _post_upload_workbook(this_sac, this_user, section, xlsx_file):
    """Upload a workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    ExcelFile = apps.get_model("audit.ExcelFile")

    if (
        ExcelFile.objects.filter(sac_id=this_sac.id, form_section=section).exists()
        and get_field_by_section(this_sac, section) is not None
    ):
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    excel_file = ExcelFile(
        file=xlsx_file,
        filename=Path("xlsx.xlsx").stem,
        user=this_user,
        sac_id=this_sac.id,
        form_section=section,
    )
    excel_file.full_clean()
    excel_file.save()

    audit_data = extract_mapping[section](excel_file.file)
    validator_mapping[section](audit_data)
    
    if section == FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED:
        this_sac.federal_awards = audit_data
    elif section == FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE:
        this_sac.findings_uniform_guidance = audit_data
    elif section == FORM_SECTIONS.FINDINGS_TEXT:
        this_sac.findings_text = audit_data
    elif section == FORM_SECTIONS.CORRECTIVE_ACTION_PLAN:
        this_sac.corrective_action_plan = audit_data
    elif section == FORM_SECTIONS.SECONDARY_AUDITORS:
        this_sac.secondary_auditors = audit_data
    elif section == FORM_SECTIONS.NOTES_TO_SEFA:
        this_sac.notes_to_sefa = audit_data
    elif section == FORM_SECTIONS.ADDITIONAL_UEIS:
        this_sac.additional_ueis = audit_data

    this_sac.save()

    logger.info("Created Federal Awards workbook upload for SAC %s", this_sac.id)
