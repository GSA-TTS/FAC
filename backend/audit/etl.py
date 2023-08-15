import logging
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
    AdditionalUei,
)
from audit.models import SingleAuditChecklist

logger = logging.getLogger(__name__)


class ETL(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        self.report_id = sac.report_id
        # MCJ QUESTION: What is the second parameter to `get` for?
        # https://docs.djangoproject.com/en/4.2/ref/models/querysets/#django.db.models.query.QuerySet.get
        audit_date = sac.general_information.get(
            "auditee_fiscal_period_start", datetime.now
        )
        self.audit_year = int(audit_date.split("-")[0])

    def load_all(self):
        load_methods = (
            self.load_general,
            self.load_secondary_auditor,
            self.load_federal_award,
            self.load_findings,
            self.load_passthrough,
            self.load_finding_texts,
            self.load_captext,
            self.load_note,
            self.load_additional_uei,
            self.load_audit_info,
        )
        for load_method in load_methods:
            try:
                load_method()
            except KeyError as key_error:
                logger.warning(
                    f"{type(key_error).__name__} in {load_method.__name__}: {key_error}"
                )

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text

        if not findings_text:
            logger.warning("No finding texts found to load")
            return

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
        if not findings_uniform_guidance:
            logger.warning("No findings found to load")
            return

        findings_uniform_guidance_entries = findings_uniform_guidance[
            "FindingsUniformGuidance"
        ]["findings_uniform_guidance_entries"]

        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            program = entry["program"]
            finding = Finding(
                award_reference=program["award_reference"],
                report_id=self.report_id,
                # finding_seq_number=entry["seq_number"],
                finding_ref_number=findings["reference_number"],
                is_material_weakness=entry["material_weakness"] == "Y",
                is_modified_opinion=entry["modified_opinion"] == "Y",
                is_other_findings=entry["other_findings"] == "Y",
                is_other_non_compliance=entry["other_matters"] == "Y",
                prior_finding_ref_numbers=None
                if "prior_references" not in findings
                else findings["prior_references"],
                is_questioned_costs=entry["questioned_costs"] == "Y",
                is_repeat_finding=(findings["repeat_prior_reference"] == "Y"),
                is_significant_deficiency=(entry["significant_deficiency"] == "Y"),
                type_requirement=(program["compliance_requirement"]),
            )
            finding.save()

    def conditional_lookup(self, dict, key, default):
        if key in dict:
            return dict[key]
        else:
            return default

    def load_federal_award(self):
        federal_awards = self.single_audit_checklist.federal_awards
        report_id = self.single_audit_checklist.report_id
        try:
            general = General.objects.get(report_id=report_id)
        except General.DoesNotExist:
            logger.error(
                f"General must be loaded before FederalAward. report_id = {report_id}"
            )
            return
        general.total_amount_expended = federal_awards["FederalAwards"].get(
            "total_amount_expended"
        )
        general.save()

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
                # CONDITIONAL
                additional_award_identification=self.conditional_lookup(
                    program, "additional_award_identification", ""
                ),
                federal_program_name=program["program_name"],
                amount_expended=program["amount_expended"],
                cluster_name=cluster["cluster_name"],
                other_cluster_name=other_cluster_name,
                state_cluster_name=state_cluster_name,
                cluster_total=cluster["cluster_total"],
                federal_program_total=program["federal_program_total"],
                is_loan=loan["is_guaranteed"] == "Y",
                loan_balance=self.conditional_lookup(
                    loan, "loan_balance_at_audit_period_end", 0
                ),
                is_direct=is_direct,
                # FIXME: This is potentially to-be-removed/historic
                is_major=program["is_major"] == "Y" if "is_major" in program else False,
                mp_audit_report_type=self.conditional_lookup(
                    program, "audit_report_type", ""
                ),
                findings_count=program["number_of_audit_findings"],
                is_passthrough_award=is_passthrough,
                passthrough_amount=subrecipient_amount,
            )
            federal_award.save()

    def load_captext(self):
        corrective_action_plan = self.single_audit_checklist.corrective_action_plan
        if (
            "corrective_action_plan_entries"
            in corrective_action_plan["CorrectiveActionPlan"]
        ):
            corrective_action_plan_entries = corrective_action_plan[
                "CorrectiveActionPlan"
            ]["corrective_action_plan_entries"]
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
        if notes_to_sefa:
            accounting_policies = notes_to_sefa["accounting_policies"]
            is_minimis_rate_used = notes_to_sefa["is_minimis_rate_used"] == "Y"
            rate_explained = notes_to_sefa["rate_explained"]
            if "notes_to_sefa_entries" in notes_to_sefa:
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
            if 'entities' in entry["direct_or_indirect_award"]:
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
        general_information = self.single_audit_checklist.general_information
        dates_by_status = self._get_dates_from_sac()
        # sac_additional_ueis = self.single_audit_checklist.additional_ueis
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
            additional_ueis=self.single_audit_checklist.additional_ueis == "Y",
            # auditee_addl_uei_list=auditee_addl_uei_list,
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
            auditor_signature_date=None,  # TODO: Field will be added by front end
            auditee_signature_date=None,  # TODO: Field will be added by front end
            fy_end_date=general_information["auditee_fiscal_period_end"],
            fy_start_date=general_information["auditee_fiscal_period_start"],
            audit_year=self.audit_year,
            audit_type=general_information["audit_type"],
            entity_type=general_information["user_provided_organization_type"],
            number_months=int(general_information["audit_period_other_months"])
            if (("audit_period_other_months" in general_information) 
                and (general_information["audit_period_other_months"] != "" 
                     or general_information["audit_period_other_months"] is None)) else None,
            audit_period_covered=general_information["audit_period_covered"],
            total_amount_expended=None,  # loaded from FederalAward
            type_audit_code="UG",
            is_public=self.single_audit_checklist.is_public,
            data_source=self.single_audit_checklist.data_source,
        )
        general.save()

    def load_secondary_auditor(self):
        secondary_auditors = self.single_audit_checklist.secondary_auditors
        # MCJ This might be empty
        if secondary_auditors:
            if "secondary_auditors_entries" in secondary_auditors["SecondaryAuditors"]:
                for secondary_auditor in secondary_auditors["SecondaryAuditors"][
                    "secondary_auditors_entries"
                ]:
                    sec_auditor = SecondaryAuditor(
                        report_id=self.single_audit_checklist.report_id,
                        auditor_ein=secondary_auditor["secondary_auditor_ein"],
                        auditor_name=secondary_auditor["secondary_auditor_name"],
                        contact_name=secondary_auditor["secondary_auditor_contact_name"],
                        contact_title=secondary_auditor["secondary_auditor_contact_title"],
                        contact_email=secondary_auditor["secondary_auditor_contact_email"],
                        contact_phone=secondary_auditor["secondary_auditor_contact_phone"],
                        address_street=secondary_auditor[
                            "secondary_auditor_address_street"
                        ],
                        address_city=secondary_auditor["secondary_auditor_address_city"],
                        address_state=secondary_auditor["secondary_auditor_address_state"],
                        address_zipcode=secondary_auditor[
                            "secondary_auditor_address_zipcode"
                        ],
                    )
                    sec_auditor.save()

    def load_additional_uei(self):
        addls = self.single_audit_checklist.additional_ueis
        if "additional_ueis_entries" in addls["AdditionalUEIs"]:
            for uei in addls["AdditionalUEIs"]["additional_ueis_entries"]:
                auei = AdditionalUei(
                    report_id=self.single_audit_checklist.report_id,
                    additional_uei=uei["additional_uei"],
                )
                auei.save()

    def load_audit_info(self):
        report_id = self.single_audit_checklist.report_id
        try:
            general = General.objects.get(report_id=report_id)
        except General.DoesNotExist:
            logger.error(
                f"General must be loaded before AuditInfo. report_id = {report_id}"
            )
            return
        audit_information = self.single_audit_checklist.audit_information
        if not audit_information:
            logger.warning("No audit info found to load")
            return
        general.gaap_results = audit_information["gaap_results"]
        general.sp_framework = audit_information["sp_framework_basis"] if "sp_framework_basis" in audit_information else None,
        general.is_sp_framework_required = (
            audit_information["is_sp_framework_required"] == "Y"
        )
        general.sp_framework_auditor_opinion = audit_information[
            "sp_framework_opinions"
        ]
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
