import logging

from django.core.management.base import BaseCommand

from audit.models import Audit, User, Schema, SingleAuditReportFile
from dissemination.models import General, Finding, FindingText, Note, AdditionalEin, AdditionalUei, CapText, \
    SecondaryAuditor, FederalAward, Passthrough

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
    One time script to migrate existing dissemination tables into the new audit table.
    """

    def handle(self, *args, **kwargs):
        # audit_report_ids = [a.report_id for a in Audit.objects.all()]

        # to_migrate = General.objects.filter(report_id__not_in=audit_report_ids)
        to_migrate = General.objects.all()
        audit_data = dict()

        for general in to_migrate:
            for handler in DISSEMINATION_HANDLERS:
                field = handler(general)
                audit_data.update(field)

            Audit.objects.create(
                event_type="MIGRATION",
                event_user=User.objects.get(email="jason.rothacker+fac@gsa.gov"),
                audit=audit_data,
                report_id=general.report_id,
                schema=Schema.objects.get_current_schema(audit_type="MIGRATION"),
                submission_status="disseminated",
                audit_type=general.audit_type,
            )
        return

## TODO: Error Handling for Not Found ect.
## Helper methods to convert dissemination tables into an audit object.
def _convert_general_information(general: General):
    return {"general_information": {
        "audit_type": general.audit_type,
        "auditee_uei": general.auditee_uei,
        "auditee_zip": general.auditee_zip,
        "auditor_ein": general.auditor_ein,
        "auditor_zip": general.auditor_zip,
        "auditee_city": general.auditee_city,
        "auditee_name": general.auditee_name,
        "auditor_city": general.auditor_city,
        "auditee_email": general.auditee_email,
        "auditee_phone": general.auditee_phone,
        "auditee_state": general.auditee_state,
        "auditor_email": general.auditor_email,
        "auditor_phone": general.auditor_phone,
        "auditor_state": general.auditor_state,
        "auditor_country": general.auditor_country,
        "auditor_firm_name": general.auditor_firm_name,
        "audit_period_covered": general.audit_period_covered,
        "auditee_contact_name": general.auditee_contact_name,
        "auditor_contact_name": general.auditor_contact_name,
        "auditee_contact_title": general.auditee_contact_title,
        "auditor_contact_title": general.auditor_contact_title,
        "auditee_address_line_1": general.auditee_address_line_1,
        "auditor_address_line_1": general.auditor_address_line_1,

        # TODO: We may want to rename these to be consistent...
        "ein": general.auditee_ein,
        "auditee_fiscal_period_end": str(general.fy_end_date),
        "auditee_fiscal_period_start": str(general.fy_start_date),
        "user_provided_organization_type": general.entity_type,
        "multiple_ueis_covered": general.is_additional_ueis == "Yes",

        # Omitted: Captured on the UI, but not disseminated.
        "auditor_ein_not_an_ssn_attestation": "MIGRATED",
        "ein_not_an_ssn_attestation": "MIGRATED",
        "is_usa_based": "MIGRATED",
        "met_spending_threshold": "MIGRATED",
        "multiple_eins_covered": "MIGRATED",
        "secondary_auditors_exist": "MIGRATED"
    }}

def _convert_findings_text(general: General):
    finding_texts = FindingText.objects.filter(report_id=general.report_id)
    converted_finding_texts = [ {
            "text_of_finding": finding_text.finding_text,
            "reference_number": finding_text.finding_ref_number,
            "contains_chart_or_table": finding_text.contains_chart_or_table,
        } for finding_text in finding_texts]
    return {"findings_text": converted_finding_texts}

def _convert_notes_to_sefa(general: General):
    notes = Note.objects.filter(report_id=general.report_id)
    converted_note = dict()
    if notes.count() > 0:
        converted_entries = [{
            "note_title": note.note_title,
            "seq_number": idx+1,  # TODO: Omitted, Consider removing
            "note_content": note.content,
            "contains_chart_or_table": note.contains_chart_or_table,
        } for idx, note in enumerate(notes)]
        converted_note = {
            "rate_explained": notes[0].rate_explained,
            "accounting_policies": notes[0].accounting_policies,
            "is_minimis_rate_used": notes[0].is_minimis_rate_used,
            "notes_to_sefa_entries": converted_entries,
        }
    return {"notes_to_sefa": converted_note}

def _convert_additional_eins(general: General):
    eins = AdditionalEin.objects.filter(report_id=general.report_id)
    converted_eins = [ein.additional_ein for ein in eins]
    return {"additional_eins": converted_eins}

def _convert_additional_ueis(general: General):
    ueis = AdditionalUei.objects.filter(report_id=general.report_id)
    converted_ueis = [uei.additional_uei for uei in ueis]
    return {"additional_ueis": converted_ueis}

def _convert_file_information(general: General):
    file = SingleAuditReportFile.objects.get(filename=f"{general.report_id}.pdf")

    return {"file_information": {
        "pages": file.component_page_numbers,
        "filename": file.filename,
    }}

def _convert_audit_information(general: General):
    return {"audit_information": {
        "agencies": general.agencies_with_prior_findings.split(","),
        "gaap_results": general.gaap_results.split(","),
        "dollar_threshold": general.dollar_threshold,
        "sp_framework_basis": general.sp_framework_basis.split(","),
        "is_low_risk_auditee": general.is_low_risk_auditee == "Yes",
        "sp_framework_opinions": general.sp_framework_opinions.split(","),
        "is_sp_framework_required": general.is_sp_framework_required == "Yes",
        "is_going_concern_included": general.is_going_concern_included == "Yes",
        "is_aicpa_audit_guide_included": general.is_aicpa_audit_guide_included == "Yes",
        "is_material_noncompliance_disclosed": general.is_material_noncompliance_disclosed == "Yes",
        "is_internal_control_deficiency_disclosed": general.is_internal_control_deficiency_disclosed == "Yes",
        "is_internal_control_material_weakness_disclosed": general.is_internal_control_material_weakness_disclosed == "Yes",
    }}

def _convert_corrective_action_plan(general: General):
    caps = CapText.objects.filter(report_id=general.report_id)
    converted_caps = [{
        "planned_action": cap.planned_action,
        "reference_number": cap.finding_ref_number,
        "contains_chart_or_table": cap.contains_chart_or_table,
    } for cap in caps]
    return {"corrective_action_plan": converted_caps}

def _convert_auditee_certification(general: General):
    return {"auditee_certification": {
            "auditee_signature": {
              "auditee_name": general.auditee_certify_name,
              "auditee_title": general.auditee_certify_title,
              "auditee_certification_date_signed": str(general.auditee_certified_date)
            },
            "auditee_certification": {
              "has_no_BII": "MIGRATED",
              "has_no_PII": "MIGRATED",
              "is_2CFR_compliant": "MIGRATED",
              "is_FAC_releasable": "MIGRATED",
              "has_engaged_auditor": "MIGRATED",
              "is_issued_and_signed": "MIGRATED",
              "is_complete_and_accurate": "MIGRATED",
              "meets_2CFR_specifications": "MIGRATED"
            }
          }}

def _convert_auditor_certification(general: General):
    return {"auditor_certification": {
            "auditor_signature": {
              "auditor_name": general.auditor_certify_name,
              "auditor_title": general.auditor_certify_title,
              "auditor_certification_date_signed": str(general.auditor_certified_date)
            },
            "auditor_certification": {
              "is_OMB_limited": "MIGRATED",
              "is_FAC_releasable": "MIGRATED",
              "is_auditee_responsible": "MIGRATED",
              "has_used_auditors_report": "MIGRATED",
              "has_no_auditee_procedures": "MIGRATED"
            }
    }}

def _convert_secondary_auditors(general: General):
    secondary_auditors = SecondaryAuditor.objects.filter(report_id=general.report_id)
    converted_secondary_auditors = [{
      "secondary_auditor_ein": sa.auditor_ein,
      "secondary_auditor_name": sa.auditor_name,
      "secondary_auditor_address_city": sa.address_city,
      "secondary_auditor_contact_name": sa.contact_name,
      "secondary_auditor_address_state": sa.address_state,
      "secondary_auditor_contact_email": sa.contact_email,
      "secondary_auditor_contact_phone": sa.contact_phone,
      "secondary_auditor_contact_title": sa.contact_title,
      "secondary_auditor_address_street": sa.address_street,
      "secondary_auditor_address_zipcode": sa.address_zipcode,
    } for sa in secondary_auditors]
    return {"secondary_auditors": converted_secondary_auditors}

def _convert_findings(general: General):
    findings = Finding.objects.filter(report_id=general.report_id)
    converted_findings = [{
      "program": {
        "award_reference": finding.award_reference,
        "compliance_requirement": finding.type_requirement,
      },
      "findings": {
        "is_valid": "MIGRATED",
        "prior_references": finding.prior_finding_ref_numbers,
        "reference_number": finding.reference_number,
        "repeat_prior_reference": finding.is_repeat_finding
      },
      "other_matters": finding.is_other_matters,
      "other_findings": finding.is_other_findings,
      "modified_opinion": finding.is_modified_opinion,
      "questioned_costs": finding.is_questioned_costs,
      "material_weakness": finding.is_material_weakness,
      "significant_deficiency": finding.is_significant_deficiency,
    } for finding in findings]
    return {"findings_uniform_guidance": converted_findings}

def _convert_federal_awards_program_names(general: General):
    awards = FederalAward.objects.filter(report_id=general.report_id)
    program_names = [award.federal_program_name for award in awards]
    converted_awards = [{
        "cluster": {
          "cluster_name": award.cluster_name,
          "cluster_total": award.cluster_total
        },
        "program": {
          "is_major": award.is_major,
          "program_name": award.federal_program_name,
          "amount_expended": award.amount_expended,
          "audit_report_type": award.audit_report_type,
          "federal_agency_prefix": award.federal_agency_prefix,
          "federal_program_total": award.federal_program_total,
          "three_digit_extension": award.federal_award_extension,
          "number_of_audit_findings": award.findings_count
        },
        "subrecipients": {
          "is_passed": award.is_passthrough_award,
          "subrecipient_amount": award.passthrough_amount
        },
        "award_reference": award.award_reference,
        "loan_or_loan_guarantee": {
          "is_guaranteed": award.is_loan,
          "loan_balance_at_audit_period_end": int(award.loan_balance)
        },
        "direct_or_indirect_award": {
          "is_direct": award.is_direct,
        }
      } for award in awards]

    return {
        "federal_awards": {
            "awards": converted_awards,
            "total_amount_expended": general.total_amount_expended,
        },
        "program_names": program_names,
    }

def _convert_tribal_consent(general: General):
    return {
        "tribal_data_consent": {
            "is_tribal_information_authorized_to_be_public": general.is_public,
            "tribal_authorization_certifying_official_name": "MIGRATED",
            "tribal_authorization_certifying_official_title": "MIGRATED"
        },
        "is_public": general.is_public,
    }

def _convert_passthrough(general: General):
    passthroughs = Passthrough.objects.filter(report_id=general.report_id)
    converted_passthroughs = [{
        "passthrough_name": pt.passthrough_name,
        "passthrough_id": pt.passthrough_id,
        "award_reference": pt.award_reference,
    } for pt in passthroughs ]
    return {"passthrough": converted_passthroughs}

def _convert_cog_oversight(general: General):
    return {
        "cognizant_agency": general.cognizant_agency,
        "oversight_agency": general.oversight_agency,
    }

def _convert_month_year(general: General):
    return {
        "audit_year": general.audit_year,
        "fy_end_month": str(general.fy_end_date.month),
        "fac_accepted_date": str(general.fac_accepted_date),
    }


DISSEMINATION_HANDLERS = [
    _convert_general_information,
    _convert_findings_text,
    _convert_notes_to_sefa,
    _convert_additional_eins,
    _convert_additional_ueis,
    _convert_corrective_action_plan,
    _convert_auditee_certification,
    _convert_auditor_certification,
    _convert_secondary_auditors,
    _convert_findings,
    _convert_federal_awards_program_names,
    _convert_audit_information,
    _convert_tribal_consent,
    _convert_passthrough,
    _convert_cog_oversight,
    _convert_month_year,
    _convert_file_information
]
