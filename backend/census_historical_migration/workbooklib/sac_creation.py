"""Fixtures for SingleAuditChecklist.

We want to create a variety of SACs in different states of
completion.
"""
from datetime import timedelta
import logging
from pathlib import Path

from django.apps import apps

from django.core.files.uploadedfile import SimpleUploadedFile

from audit.intakelib import (
    extract_federal_awards,
    extract_audit_findings as extract_findings_uniform_guidance,
    extract_audit_findings_text as extract_findings_text,
    extract_corrective_action_plan,
    extract_secondary_auditors,
    extract_notes_to_sefa,
    extract_additional_ueis,
    extract_additional_eins,
)
import audit.validators

from audit.fixtures.excel import FORM_SECTIONS
from audit.models import SingleAuditChecklist, ExcelFile
from .transformers import clean_gen, make_report_id, str_to_date
from ..models import (
    ELECAUDITHEADER as Gen,
    ELECAUDITS as Cfda,
    ELECAUDITFINDINGS as Finding,
)


logger = logging.getLogger(__name__)


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
    FORM_SECTIONS.ADDITIONAL_EINS: extract_additional_eins,
}

validator_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: audit.validators.validate_federal_award_json,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: audit.validators.validate_findings_uniform_guidance_json,
    FORM_SECTIONS.FINDINGS_TEXT: audit.validators.validate_findings_text_json,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: audit.validators.validate_corrective_action_plan_json,
    FORM_SECTIONS.SECONDARY_AUDITORS: audit.validators.validate_secondary_auditors_json,
    FORM_SECTIONS.NOTES_TO_SEFA: audit.validators.validate_notes_to_sefa_json,
    FORM_SECTIONS.ADDITIONAL_UEIS: audit.validators.validate_additional_ueis_json,
    FORM_SECTIONS.ADDITIONAL_EINS: audit.validators.validate_additional_eins_json,
    "PDF": audit.validators.validate_single_audit_report_file,
}


def _period_covered(s):
    return {"A": "annual", "B": "biennial", "O": "other"}[s]


def _census_audit_type(s):
    return {
        "S": "single-audit",
        "P": "program-specific",
        "A": "alternative-compliance-engagement",
    }[s]


def add_hyphen_to_zip(zip):
    strzip = str(zip)
    if len(strzip) == 5:
        return strzip
    elif len(strzip) == 9:
        return f"{strzip[0:5]}-{strzip[5:9]}"
    else:
        logger.info("ZIP IS MALFORMED IN WORKBOOKS E2E / SAC_CREATION")
        return strzip


def get_general_information(gen):
    """Create a fake general_information object."""
    # TODO: can we generate this object from the schema definition in
    # schemas/output/GeneralInformation.schema.json?
    gobj = gen
    auditee_fiscal_period_end = str_to_date(gobj.FYENDDATE).strftime("%Y-%m-%d")
    auditee_fiscal_period_start = (
        str_to_date(gobj.FYENDDATE) - timedelta(days=365)
    ).strftime("%Y-%m-%d")
    if gobj.CPACOUNTRY == "US":
        cpacountry = "USA"
    elif gobj.CPACOUNTRY != "US":
        cpacountry = "non-USA"

    general_information = {
        "auditee_fiscal_period_start": auditee_fiscal_period_start,
        "auditee_fiscal_period_end": auditee_fiscal_period_end,
        "audit_period_covered": _period_covered(gobj.PERIODCOVERED),
        "audit_type": _census_audit_type(gobj.AUDITTYPE),
        "auditee_address_line_1": gobj.STREET1,
        "auditee_city": gobj.CITY,
        "auditee_contact_name": gobj.AUDITEECONTACT,
        "auditee_contact_title": gobj.AUDITEETITLE,
        "auditee_email": gobj.AUDITEEEMAIL,
        "auditee_name": gobj.AUDITEENAME,
        "auditee_phone": gobj.AUDITEEPHONE,
        # TODO: when we include territories in our valid states, remove this restriction
        "auditee_state": gobj.STATE,
        # TODO: this is GSA's UEI. We could do better at making random choices that
        # pass the schema's complex regex validation
        "auditee_uei": gobj.UEI,
        "auditee_zip": gobj.ZIPCODE,
        "auditor_address_line_1": gobj.CPASTREET1,
        "auditor_city": gobj.CPACITY,
        "auditor_contact_name": gobj.CPACONTACT,
        "auditor_contact_title": gobj.CPATITLE,
        "auditor_country": cpacountry,
        "auditor_ein": gobj.AUDITOR_EIN,
        "auditor_ein_not_an_ssn_attestation": True,
        "auditor_email": gobj.CPAEMAIL if gobj.CPAEMAIL else "noemailfound@noemail.com",
        "auditor_firm_name": gobj.CPAFIRMNAME,
        "auditor_phone": gobj.CPAPHONE,
        # TODO: when we include territories in our valid states, remove this restriction
        "auditor_state": gobj.CPASTATE,
        "auditor_zip": gobj.CPAZIPCODE,
        "ein": gobj.EIN,
        "ein_not_an_ssn_attestation": True,
        "is_usa_based": True,
        "met_spending_threshold": True,
        "multiple_eins_covered": True if gobj.MULTIPLEEINS == "Y" else False,
        "multiple_ueis_covered": True if gobj.MULTIPLEUEIS == "Y" else False,
        # TODO: could improve this by randomly choosing from the enum of possible values
        "user_provided_organization_type": "unknown",
        "secondary_auditors_exist": True if gobj.MULTIPLE_CPAS == "Y" else False,
    }

    # TODO verify that our created object validates against the schema
    # audit.validators.validate_general_information_complete_json(general_information)

    return general_information


# TODO: Pull this from actual information.
def get_audit_information(gen: Gen):
    gobj = gen
    cfdas = Cfda.objects.filter(DBKEY=gen.DBKEY, AUDITYEAR=gen.AUDITYEAR)
    findings = Finding.objects.filter(DBKEY=gen.DBKEY, AUDITYEAR=gen.AUDITYEAR)

    agencies = []
    cfda: Cfda
    for cfda in cfdas:
        agency = int((cfda.CFDA).split(".")[0])
        agency_str = str(agency) if agency >= 10 else "0" + str(agency)
        agencies.append(agency_str)

    finding: Finding
    gaap_results = {}
    # THIS IS NOT A GOOD WAY TO DO THIS, BUT IT IS CLOSE.
    # IT IS FOR TEST DATA...
    for finding in findings:
        if finding.MODIFIEDOPINION == "Y":
            gaap_results["unmodified_opinion"] = 1
        if finding.MATERIALWEAKNESS == "Y":
            gaap_results["adverse_opinion"] = 1
        if finding.SIGNIFICANTDEFICIENCY == "Y":
            gaap_results["disclaimer_of_opinion"] = 1

    audit_information = {
        "agencies": agencies,
        "dollar_threshold": 750000,
        "gaap_results": list(gaap_results.keys()),
        "is_aicpa_audit_guide_included": True
        if gobj.REPORTABLECONDITION == "Y"
        else False,
        "is_going_concern_included": True if gobj.GOINGCONCERN == "Y" else False,
        "is_internal_control_deficiency_disclosed": True
        if gobj.MATERIALWEAKNESS == "Y"
        else False,
        "is_internal_control_material_weakness_disclosed": True
        if gobj.MATERIALWEAKNESS_MP == "Y"
        else False,
        "is_low_risk_auditee": False,
        "is_material_noncompliance_disclosed": True
        if gobj.MATERIALNONCOMPLIANCE == "Y"
        else False,
    }

    # TODO Uncomment this
    # audit.validators.validate_audit_information_json(audit_information)

    return audit_information


def create_sac(user, gen):
    clean_gen(gen)

    """Create a single example SAC."""
    report_id = make_report_id(gen.AUDITYEAR, gen.FYENDDATE, gen.DBKEY)

    try:
        exists = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    sac = SingleAuditChecklist(
        report_id=report_id,
        submitted_by=user,
    )

    sac.general_information = get_general_information(gen)
    sac.audit_information = get_audit_information(gen)
    set_auditee_cerification(sac)
    set_auditor_certification(sac)
    sac.data_source = "CENSUS"
    # sac.save()

    logger.info("Created single audit checklist %s", sac)
    return sac


def set_auditor_certification(sac):
    sac.auditor_certification = {}
    sac.auditor_certification["auditor_signature"] = {}
    sac.auditor_certification["auditor_signature"][
        "auditor_name"
    ] = "Alice the Auditor Name"
    sac.auditor_certification["auditor_signature"][
        "auditor_title"
    ] = "Alice the Auditor Signature"


def set_auditee_cerification(sac):
    sac.auditee_certification = {}
    sac.auditee_certification["auditee_signature"] = {}
    sac.auditee_certification["auditee_signature"][
        "auditee_name"
    ] = "Bob the Auditee Name"
    sac.auditee_certification["auditee_signature"][
        "auditee_title"
    ] = "Bob the Auditee Signature"


def _create_test_sac(user, auditee_name, dbkey):
    """Create a single example SAC."""
    report_id = make_report_id("2022", "04/01/2022", dbkey)

    try:
        exists = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=get_general_information(dbkey, auditee_name),
        audit_information=get_audit_information(dbkey, auditee_name),
    )
    # Set a TEST report id for this data
    sac.report_id = report_id

    Access = apps.get_model("audit.Access")
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )

    # We need these to be different.
    Access.objects.create(
        sac=sac,
        user=user,
        email="bob_the_auditee_official@auditee.org",  # user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email="bob_the_auditor_official@auditor.org",  # user.email,
        role="certifying_auditor_contact",
    )

    sac.auditee_certification = {}
    sac.auditee_certification["auditee_signature"] = {}
    sac.auditee_certification["auditee_signature"][
        "auditee_name"
    ] = "Bob the Auditee Name"
    sac.auditee_certification["auditee_signature"][
        "auditee_title"
    ] = "Bob the Auditee Signature"

    sac.auditor_certification = {}
    sac.auditor_certification["auditor_signature"] = {}
    sac.auditor_certification["auditor_signature"][
        "auditor_name"
    ] = "Alice the Auditor Name"
    sac.auditor_certification["auditor_signature"][
        "auditor_title"
    ] = "Alice the Auditor Signature"

    sac.data_source = "TSTDAT"
    sac.save()

    logger.info("Created single audit checklist %s", sac)
    return sac


def _make_excel_file(filename, f_obj):
    content = f_obj.read()
    f_obj.seek(0)
    file = SimpleUploadedFile(filename, content, "application/vnd.ms-excel")
    return file


def _post_upload_pdf(this_sac, this_user, pdf_filename):
    """Upload a workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    PDFFile = apps.get_model("audit.SingleAuditReportFile")

    if PDFFile.objects.filter(sac_id=this_sac.id).exists():
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    with open(pdf_filename, "rb") as f:
        content = f.read()
    file = SimpleUploadedFile(pdf_filename, content, "application/pdf")
    print(file.__dict__)
    pdf_file = PDFFile(
        file=file,
        component_page_numbers={
            "financial_statements": 1,
            "financial_statements_opinion": 2,
            "schedule_expenditures": 3,
            "schedule_expenditures_opinion": 4,
            "uniform_guidance_control": 5,
            "uniform_guidance_compliance": 6,
            "GAS_control": 6,
            "GAS_compliance": 7,
            "schedule_findings": 8,
        },
        filename=Path(pdf_filename).stem,
        user=this_user,
        sac_id=this_sac.id,
    )

    validator_mapping["PDF"](pdf_file.file)

    pdf_file.full_clean()
    pdf_file.save()

    this_sac.save()


def make_valid_ir_and_update_sac(this_sac, this_user, section, xlsx_file):
    """Make an IR for the section, validate and save the json into the sac.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """

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

    # Not needed for ;pading historical data
    # excel_file.full_clean()
    # excel_file.save()

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
    elif section == FORM_SECTIONS.ADDITIONAL_EINS:
        this_sac.additional_eins = audit_data

    this_sac.save()

    logger.info(f"Created {section} workbook upload for SAC {this_sac.id}")
