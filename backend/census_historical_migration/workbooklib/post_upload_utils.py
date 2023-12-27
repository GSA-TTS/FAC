import logging
from django.apps import apps

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
}


def record_dummy_pdf_object(this_sac, this_user):
    """Create a dummy PDFFile object for this SAC.
    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    PDFFile = apps.get_model("audit.SingleAuditReportFile")

    if PDFFile.objects.filter(sac_id=this_sac.id).exists():
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return
    # we are not uploading PDF for historic data migration
    # but we need to create a PDFFile object to pass validation
    pdf_file = PDFFile(
        file=None,
        component_page_numbers=None,
        filename=None,
        user=this_user,
        sac_id=this_sac.id,
    )

    pdf_file.save()
    this_sac.save()


def post_upload_workbook(this_sac, section, xlsx_file):
    """Upload a workbook for this SAC."""

    audit_data = extract_mapping[section](xlsx_file, is_gsa_migration=True)
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
