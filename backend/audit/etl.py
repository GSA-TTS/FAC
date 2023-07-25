from datetime import datetime

from dissemination.models import (
    FindingText,
    Finding,
    FederalAward,
    CapText,
    Note,
    Revision,
    Passthrough,
    General,
    SecondaryAuditor,
)
from audit.models import SingleAuditChecklist


class ETL(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        self.report_id = sac.report_id
        audit_date = sac.general_information.get(
            "auditee_fiscal_period_start", datetime.now
        )
        self.audit_year = int(audit_date.split("-")[0])

    def load_all(self):
        # TODO: Wrap each method call in try/except to collect errors.
        self.load_general()
        self.load_secondary_auditor()
        self.load_federal_award()
        self.load_findings()
        self.load_passthrough()
        self.load_finding_texts()
        self.load_captext()
        # self.load_audit_info() TODO uncomment once the frontend is available

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text
        findings_text_entries = findings_text["FindingsText"]["findings_text_entries"]
        for entry in findings_text_entries:
            finding_text_ = FindingText(
                report_id=self.report_id,
                finding_ref_number=entry["reference_number"],
                contains_chart_or_table=entry["contains_chart_or_table"] == "Y",
                finding_text=entry["text_of_finding"],
            )
            finding_text_.save()

    def load_findings(self):
        findings_uniform_guidance = (
            self.single_audit_checklist.findings_uniform_guidance
        )
        findings_uniform_guidance_entries = findings_uniform_guidance[
            "FindingsUniformGuidance"
        ]["findings_uniform_guidance_entries"]

        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            finding = Finding(
                award_reference=entry["award_reference"],
                report_id=self.report_id,
                finding_seq_number=entry["seq_number"],
                finding_ref_number=findings["reference_number"],
                is_material_weakness=entry["material_weakness"] == "Y",
                is_modified_opinion=entry["modified_opinion"] == "Y",
                is_other_findings=entry["other_findings"] == "Y",
                is_other_non_compliance=entry["other_findings"] == "Y",
                prior_finding_ref_numbers=findings.get("prior_references"),
                is_questioned_costs=entry["questioned_costs"] == "Y",
                is_repeat_finding=(findings["repeat_prior_reference"] == "Y"),
                is_significant_deficiency=(entry["significant_deficiency"] == "Y"),
                type_requirement=(entry["program"]["compliance_requirement"]),
            )
            finding.save()

    def load_federal_award(self):
        federal_awards = self.single_audit_checklist.federal_awards
        for entry in federal_awards["FederalAwards"]["federal_awards"]:
            program = entry["program"]
            loan = entry["loan_or_loan_guarantee"]
            is_direct = entry["direct_or_indirect_award"]["is_direct"] == "Y"
            is_passthrough = entry["subrecipients"]["is_passed"] == "Y"
            cluster = entry["cluster"]
            subrecipient_amount = entry["subrecipients"].get("subrecipient_amount")
            state_cluster_name = cluster.get("state_cluster_name")
            other_cluster_name = cluster.get("other_cluster_name")
            federal_award = FederalAward(
                report_id=self.report_id,
                award_reference=entry["award_reference"],
                federal_agency_prefix=program["federal_agency_prefix"],
                federal_award_extension=program["three_digit_extension"],
                additional_award_identification=program[
                    "additional_award_identification"
                ],
                federal_program_name=program["program_name"],
                amount_expended=program["amount_expended"],
                cluster_name=cluster["cluster_name"],
                other_cluster_name=other_cluster_name,
                state_cluster_name=state_cluster_name,
                cluster_total=cluster["cluster_total"],
                federal_program_total=program["federal_program_total"],
                is_loan=loan["is_guaranteed"] == "Y",
                loan_balance=loan["loan_balance_at_audit_period_end"],
                is_direct=is_direct,
                is_major=program["is_major"] == "Y",
                mp_audit_report_type=program["audit_report_type"],
                findings_count=program["number_of_audit_findings"],
                is_passthrough_award=is_passthrough,
                passthrough_amount=subrecipient_amount,
                type_requirement=None,  # TODO: What is this?
            )
            federal_award.save()

    def load_captext(self):
        corrective_action_plan = self.single_audit_checklist.corrective_action_plan
        corrective_action_plan_entries = corrective_action_plan["CorrectiveActionPlan"][
            "corrective_action_plan_entries"
        ]
        for entry in corrective_action_plan_entries:
            cap_text = CapText(
                report_id=self.report_id,
                finding_ref_number=entry["reference_number"],
                contains_chart_or_table=entry["contains_chart_or_table"] == "Y",
                planned_action=entry["planned_action"],
            )
            cap_text.save()

    def load_note(self):
        notes_to_sefa = self.single_audit_checklist.notes_to_sefa["NotesToSefa"]
        accounting_policies = notes_to_sefa["accounting_policies"]
        is_minimis_rate_used = notes_to_sefa["is_minimis_rate_used"]
        rate_explained = notes_to_sefa["rate_explained"]
        entries = notes_to_sefa["notes_to_sefa_entries"]
        if not entries:
            note = Note(
                report_id=self.report_id,
                accounting_policies=accounting_policies,
                is_minimis_rate_used=is_minimis_rate_used,
                rate_explained=rate_explained,
            )
            note.save()
        else:
            for entry in entries:
                note = Note(
                    report_id=self.report_id,
                    note_seq_number=entry["seq_number"],
                    content=entry["note_content"],
                    note_title=entry["note_title"],
                    accounting_policies=accounting_policies,
                    is_minimis_rate_used=is_minimis_rate_used,
                    rate_explained=rate_explained,
                )
                note.save()

    def load_revision(self):
        revision = Revision(
            findings=None,  # TODO: Where does this come from?
            revision_id=None,  # TODO: Where does this come from?
            federal_awards=None,  # TODO: Where does this come from?
            general_info_explain=None,  # TODO: Where does this come from?
            federal_awards_explain=None,  # TODO: Where does this come from?
            notes_to_sefa_explain=None,  # TODO: Where does this come from?
            audit_info_explain=None,  # TODO: Where does this come from?
            findings_explain=None,  # TODO: Where does this come from?
            findings_text_explain=None,  # TODO: Where does this come from?
            cap_explain=None,  # TODO: Where does this come from?
            other_explain=None,  # TODO: Where does this come from?
            audit_info=None,  # TODO: Where does this come from?
            notes_to_sefa=None,  # TODO: Where does this come from?
            findings_tex=None,  # TODO: Where does this come from?
            cap=None,  # TODO: Where does this come from?
            other=None,  # TODO: Where does this come from?
            general_info=None,  # TODO: Where does this come from?
            audit_year=self.audit_year,
            report_id=self.report_id,
        )
        revision.save()

    def load_passthrough(self):
        federal_awards = self.single_audit_checklist.federal_awards
        for entry in federal_awards["FederalAwards"]["federal_awards"]:
            for entity in entry["direct_or_indirect_award"]["entities"]:
                passthrough = Passthrough(
                    award_reference=entry["award_reference"],
                    report_id=self.report_id,
                    passthrough_id=entity["passthrough_identifying_number"],
                    passthrough_name=entity["passthrough_name"],
                )
                passthrough.save()

    def _get_dates_from_sac(self):
        return_dict = dict()
        sac = self.single_audit_checklist
        for status_choice in sac.STATUS_CHOICES:
            status = status_choice[0]
            if status in sac.transition_name:
                return_dict[status] = sac.get_transition_date(status)
            else:
                return_dict[status] = None
        return return_dict

    def load_general(self):
        # TODO: Use the mixin to access general_information fields once that code
        #       is merged.
        general_information = self.single_audit_checklist.general_information
        dates_by_status = self._get_dates_from_sac()
        general = General(
            report_id=self.report_id,
            auditee_certify_name=None,  # TODO: Where does this come from?
            auditee_certify_title=None,  # TODO: Where does this come from?
            auditee_contact_name=general_information["auditee_contact_name"],
            auditee_email=general_information["auditee_email"],
            auditee_name=general_information["auditee_name"],
            auditee_phone=general_information["auditee_phone"],
            auditee_contact_title=general_information["auditee_contact_title"],
            auditee_address_line_1=general_information["auditee_address_line_1"],
            auditee_city=general_information["auditee_city"],
            auditee_state=general_information["auditee_state"],
            auditee_ein=general_information["ein"],
            auditee_uei=general_information["auditee_uei"],
            auditee_addl_uei_list=[],
            auditee_zip=general_information["auditee_zip"],
            auditor_phone=general_information["auditor_phone"],
            auditor_state=general_information["auditor_state"],
            auditor_city=general_information["auditor_city"],
            auditor_contact_title=general_information["auditor_contact_title"],
            auditor_address_line_1=general_information["auditor_address_line_1"],
            auditor_zip=general_information["auditor_zip"],
            auditor_country=general_information["auditor_country"],
            auditor_contact_name=general_information["auditor_contact_name"],
            auditor_email=general_information["auditor_email"],
            auditor_firm_name=general_information["auditor_firm_name"],
            auditor_foreign_addr=None,  # TODO:  What does this look like in the incoming json?
            auditor_ein=general_information["auditor_ein"],
            cognizant_agency=None,  # TODO: https://github.com/GSA-TTS/FAC/issues/1218
            oversight_agency=None,  # TODO: https://github.com/GSA-TTS/FAC/issues/1218
            initial_date_received=self.single_audit_checklist.date_created,
            ready_for_certification_date=dates_by_status[
                self.single_audit_checklist.STATUS.READY_FOR_CERTIFICATION
            ],
            auditor_certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.AUDITOR_CERTIFIED
            ],
            auditee_certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.AUDITEE_CERTIFIED
            ],
            certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.CERTIFIED
            ],
            submitted_date=dates_by_status[
                self.single_audit_checklist.STATUS.SUBMITTED
            ],
            fy_end_date=general_information["auditee_fiscal_period_end"],
            fy_start_date=general_information["auditee_fiscal_period_start"],
            audit_year=self.audit_year,
            audit_type=general_information["audit_type"],
            entity_type=general_information["user_provided_organization_type"],
            number_months=None,  # TODO: Where does this come from?
            audit_period_covered=general_information["audit_period_covered"],
            report_required=None,  # TODO: Notes say this hasn't been used since 2008.
            total_fed_expenditures=None,  # TODO: Where does this come from?
            type_report_major_program=None,  # TODO: Where does this come from?
            type_audit_code="UG",
            is_public=None,  # Should be coming from SingleAuditChecklist
            data_source="G-FAC",
        )
        general.save()

    def load_secondary_auditor(self):
        secondary_auditors = self.single_audit_checklist.secondary_auditors

        for secondary_auditor in secondary_auditors["SecondaryAuditors"][
            "secondary_auditors_entries"
        ]["items"]:
            sec_auditor = SecondaryAuditor(
                report_id=self.single_audit_checklist.report_id,
                auditor_seq_number=secondary_auditor["secondary_auditor_seq_number"],
                auditor_ein=secondary_auditor["secondary_auditor_ein"],
                auditor_name=secondary_auditor["secondary_auditor_name"],
                contact_name=secondary_auditor["secondary_auditor_contact_name"],
                contact_title=secondary_auditor["secondary_auditor_contact_title"],
                contact_email=secondary_auditor["secondary_auditor_contact_email"],
                contact_phone=secondary_auditor["secondary_auditor_contact_phone"],
                address_street=secondary_auditor["secondary_auditor_address_street"],
                address_city=secondary_auditor["secondary_auditor_address_city"],
                address_state=secondary_auditor["secondary_auditor_address_state"],
                address_zipcode=secondary_auditor["secondary_auditor_address_zipcode"],
            )
            sec_auditor.save()

    def load_audit_info(self):
        general = General.objects.get(report_id=self.single_audit_checklist.report_id)
        audit_information = self.single_audit_checklist.audit_information

        general.gaap_results = audit_information["gaap_results"]
        """
            TODO:
            Missing in schema
            general.sp_framework = audit_information[]
            general.is_sp_framework_required = audit_information[]
            general.sp_framework_auditor_opinion = audit_information[]
        """
        general.is_going_concern = audit_information["is_going_concern_included"] == "Y"
        general.is_significant_deficiency = (
            audit_information["is_internal_control_deficiency_disclosed"] == "Y"
        )
        general.is_material_weakness = (
            audit_information["is_internal_control_material_weakness_disclosed"] == "Y"
        )
        general.is_material_noncompliance = (
            audit_information["is_material_noncompliance_disclosed"] == "Y"
        )
        general.is_duplicate_reports = (
            audit_information["is_aicpa_audit_guide_included"] == "Y"
        )
        general.dollar_threshold = audit_information["dollar_threshold"]
        general.is_low_risk = audit_information["is_low_risk_auditee"] == "Y"
        general.agencies_with_prior_findings = audit_information["agencies"]

        general.save()
