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
        component_page_numbers={  # FIXME MSHD- see ticket #2912
            "financial_statements": -1,
            "financial_statements_opinion": -1,
            "schedule_expenditures": -1,
            "schedule_expenditures_opinion": -1,
            "uniform_guidance_control": -1,
            "uniform_guidance_compliance": -1,
            "GAS_control": -1,
            "GAS_compliance": -1,
            "schedule_findings": -1,
        },
        filename=Path(pdf_filename).stem,
        user=this_user,
        sac_id=this_sac.id,
    )

    validator_mapping["PDF"](pdf_file.file)

    pdf_file.full_clean()
    pdf_file.save()

    this_sac.save()


def _post_upload_workbook(this_sac, section, xlsx_file):
    """Upload a workbook for this SAC."""

    audit_data = extract_mapping[section](xlsx_file)
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
