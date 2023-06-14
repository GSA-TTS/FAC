from data_distro.models import FindingText, Finding, CapText
from .models import SingleAuditChecklist

class ETL(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        general_information = sac.general_information
        self.report_id = sac.report_id
        audit_date = general_information["auditee_fiscal_period_start"]
        self.audit_year = audit_date.split("-")[0]
        self.is_public = True # TODO: update this when necessary

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text
        findings_text_entries = findings_text["FindingsText"]["findings_text_entries"]
        sequence_number = 1 # TODO: replace this when we are getting sequence number in JSON

        for entry in findings_text_entries:
            reference_number = entry["reference_number"]
            charts_tables = entry["contains_chart_or_table"] == "Y"
            text = entry["text_of_finding"]
            finding_text = FindingText(
                charts_tables = charts_tables,
                finding_ref_number = reference_number,
                sequence_number = sequence_number,
                text = text,
                dbkey = None,
                audit_year = self.audit_year,
                is_public = self.is_public,
                report_id = self.report_id
            )
            sequence_number += 1
            finding_text.save()

    def load_findings(self):
        findings_uniform_guidance = self.single_audit_checklist.findings_uniform_guidance
        findings_uniform_guidance_entries = (
                findings_uniform_guidance
                ["FindingsUniformGuidance"]
                ["findings_uniform_guidance_entries"]
            )
        audit_id = 1 # TODO: replace this with correct value

        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            reference_number = findings["reference_number"]
            finding = Finding(
                finding_ref_number = reference_number,
                audit_id = audit_id,
                audit_findings_id = audit_id, # TODO: Replace with correct value
                prior_finding_ref_numbers = findings.get("prior_references"),
                modified_opinion = entry["modified_opinion"] == "Y",
                other_non_compliance = entry["other_matters"] == "Y",
                material_weakness = entry["material_weakness"] == "Y",
                significant_deficiency = (
                    entry["significant_deficiency"] == "Y"
                ),
                other_findings = entry["other_findings"] == "Y",
                questioned_costs = entry["questioned_costs"] == "Y",
                repeat_finding = (
                    findings["repeat_prior_reference"] == "Y"
                ),
                type_requirement = (
                    entry["program"]["compliance_requirement"]
                ),
                audit_year = self.audit_year,
                dbkey = None,
                is_public = self.is_public,
                report_id = self.report_id
            )
            finding.save()
            audit_id += 1 # TODO: remove this
    
    def load_captext(self):
        corrective_action_plan = (
            self.single_audit_checklist.corrective_action_plan
        )
        corrective_action_plan_entries = (
            corrective_action_plan
            ["CorrectiveActionPlan"]
            ["corrective_action_plan_entries"]
        )
        for entry in corrective_action_plan_entries:
            cap_text = CapText(
                finding_ref_number = entry["reference_number"],
                charts_tables = entry["contains_chart_or_table"] == "Y",
                sequence_number = 1, # TODO: fix this as sonn as we know what it should be
                text = entry["planned_action"],
                dbkey = None,
                audit_year = self.audit_year,
                is_public = True, # TODO: fix this when necessary
                report_id = self.report_id
            )
            cap_text.save()

