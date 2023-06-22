from dissemination.models import ( 
    FindingText, 
    Finding, 
    FederalAward,
    CapText,
    Note,
    Revision,
    Passthrough,
    General
)
from .models import SingleAuditChecklist

class ETL(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        self.general_information = sac.general_information
        self.report_id = sac.report_id
        audit_date = self.general_information["auditee_fiscal_period_start"]
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
                # dbkey = None,
                # audit_year = self.audit_year,
                # is_public = self.is_public,
                # report_id = self.report_id
            )
            sequence_number += 1 # TODO: Remove this.
            finding_text.save()

    def load_findings(self):
        findings_uniform_guidance = (
            self.single_audit_checklist.findings_uniform_guidance
        )
        findings_uniform_guidance_entries = (
                findings_uniform_guidance
                ["FindingsUniformGuidance"]
                ["findings_uniform_guidance_entries"]
            )

        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            reference_number = findings["reference_number"]
            prior_references = findings.get("prior_references")
            finding = Finding(
                finding_ref_number = reference_number,
                prior_finding_ref_numbers = prior_references,
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
                report_id = self.report_id,
                award_id = entry.get("seq_number", 1), # TODO: This will be the sequence number
                # audit_id = audit_id,
                # audit_findings_id = audit_id,
                # audit_year = self.audit_year,
                # dbkey = None,
                # is_public = self.is_public,
            )
            finding.save()
    
    def load_federal_award(self):
        federal_awards = self.single_audit_checklist.federal_awards
        for entry in federal_awards(
            ["FederalAwards"]["federal_awards"]
        ):
            program = entry["program"]
            agency_cfda = (
                f"{entry['federal_agency_prefix']}."
                f"{entry['three_digit_extension']}"
            )
            loan = entry["loan_or_loan_guarantee"]
            loans = loan["is_guaranteed"] == "Y"
            is_direct = (
                entry["direct_or_indirect_award"]
                ["is_direct"] == "Y"
            )
            is_passthrough = (
                entry["subrecipients"]["is_passed"] == "Y"
            )
            is_major = program["is_major"] == "Y"
            cluster = entry["cluster"]
            subrecipient_amount = (
                entry["subrecipients"]
                .get("subrecipient_amount", None)
            )
            loan_balance = (
                loan.get("loan_balance_at_audit_period_end", None)
            )
            state_cluster_name = (
                cluster.get("state_cluster_name", None)
            )
            other_cluster_name = (
                cluster.get("other_cluster_name", None)
            )
            federal_award = FederalAward(
                award_id = entry.get("seq_number", 1),
                federal_program_name = program["program_name"],
                agency_name = "?", # TODO: Where is this coming from?
                agency_cfda = agency_cfda,
                award_identification = (
                    program["additional_award_identification"]
                ),
                research_and_development = None, # TODO: Where does this come from?
                loans = loans,
                arra = None, # TODO: Where does this come from?
                direct = is_direct,
                passthrough_award = is_passthrough,
                major_program = is_major,
                amount = program["amount_expended"],
                program_total = program["federal_program_total"],
                cluster_total = cluster["cluster_total"],
                passthrough_amount = subrecipient_amount,
                loan_balance = loan_balance,
                cluster_name = cluster["cluster_name"],
                state_cluster_name = state_cluster_name,
                other_cluster_name = other_cluster_name,
                type_requirement = None, # TODO: What is this?
                type_report_major_program = (
                    program["audit_report_type"]
                ),
                findings_page = None, # TODO: Where does this come from?
                findings_count = program["number_of_audit_findings"],
                questioned_costs = None, # TODO: Where does this come from?
                report_id = self.report_id                
            )
            federal_award.save()
    
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
                sequence_number = -1, # TODO: fix this as sonn as we know what it should be
                text = entry["planned_action"],
                # dbkey = None,
                # audit_year = self.audit_year,
                # is_public = True, # TODO: fix this when necessary
                # report_id = self.report_id
            )
            cap_text.save()

    def load_note(self):
        note = Note(
            type_id = "", # TODO: What is this?
            report_id = self.report_id,
            version = "", # TODO: What is this?
            sequence_number = -1, # TODO: Where does this come from?
            note_index = -1, # TODO: Where does this come from?
            content = "", # TODO: Where does this come from?
            title = "", # TODO: Where does this come from?
        )
        note.save()

    def load_revision(self):
        revision = Revision(
            findings = None, # TODO: Where does this come from?
            revision_id = None, # TODO: Where does this come from?
            federal_awards = None, # TODO: Where does this come from?
            general_info_explain = None, # TODO: Where does this come from?
            federal_awards_explain = None, # TODO: Where does this come from?
            notes_to_sefa_explain = None, # TODO: Where does this come from?
            audit_info_explain = None, # TODO: Where does this come from?
            findings_explain = None, # TODO: Where does this come from?
            findings_text_explain = None, # TODO: Where does this come from?
            cap_explain = None, # TODO: Where does this come from?
            other_explain = None, # TODO: Where does this come from?
            audit_info = None, # TODO: Where does this come from?
            notes_to_sefa = None, # TODO: Where does this come from?
            findings_tex = None, # TODO: Where does this come from?
            cap = None, # TODO: Where does this come from?
            other = None, # TODO: Where does this come from?
            general_info = None, # TODO: Where does this come from?
            audit_year = self.audit_year,
            report_id = self.report_id
        )
        revision.save()

    def load_passthrough(self):
        passthrough = Passthrough(
            passthrough_name = None, # TODO: Where does this come from?
            passthrough_id = None, # TODO: Where does this come from?
            audit_id = -1, # TODO: Where does this come from?
            audit_year = self.audit_year,
            report_id = self.report_id
        )
        passthrough.save()

    def load_general(self):
        general = General(
            report_id = self.report_id,
            auditee_certify_name = None, # TODO: Where does this come from?
            auditee_certify_title = None, # TODO: Where does this come from?
            auditee_contact = self.general_information["auditee_contact_name"],
            auditee_email = self.general_information["auditee_email"],
            auditee_fax = None, # TODO: Notes say this field is not in use.
            auditee_name = self.general_information["auditee_name"],
            auditee_name_title = self.general_information["auditee_contact_title"],
            auditee_phone = self.general_information["auditee_phone"],
            auditee_title = self.general_information["auditee_contact_title"],
            auditee_street_1 = self.general_information["auditee_address_line_1"],
            auditee_street_2 = None, # TODO: Notes say thins field is not in use.
        )
