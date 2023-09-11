import logging
from datetime import datetime

from dissemination.models import (
    FindingText,
    Finding,
    FederalAward,
    CapText,
    Note,
    Passthrough,
    General,
    SecondaryAuditor,
    AdditionalUei,
)
from audit.models import SingleAuditChecklist

logger = logging.getLogger(__name__)


class IntakeToDissemination(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        self.report_id = sac.report_id
        audit_date = sac.general_information.get(
            "auditee_fiscal_period_start", datetime.now
        )
        self.audit_year = int(audit_date.split("-")[0])
        self.loaded_objects: dict[str, list] = {}

    def load_all(self):
        load_methods = {
            "Generals": self.load_general,
            "SecondaryAuditors": self.load_secondary_auditor,
            "FederalAwards": self.load_federal_award,
            "Findings": self.load_findings,
            "FindingTexts": self.load_finding_texts,
            "Passthroughs": self.load_passthrough,
            "CapTexts": self.load_captext,
            "Notes": self.load_notes,
            "AdditionalUEIs": self.load_additional_ueis,
        }
        for _, load_method in load_methods.items():
            try:
                # Each method writes results into self.loaded_objects
                load_method()
            except KeyError as key_error:
                logger.warning(
                    f"{type(key_error).__name__} in {load_method.__name__}: {key_error}"
                )
        return self.loaded_objects

    def get_dissemination_objects(self):
        return self.loaded_objects

    def save_dissemination_objects(self):
        for key in self.loaded_objects.keys():
            for o in self.loaded_objects[key]:
                o.save()

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text

        if not findings_text:
            logger.warning("No finding texts found to load")
            return

        findings_text_entries = findings_text.get("FindingsText", {}).get(
            "findings_text_entries", []
        )
        findings_text_objects = []

        for entry in findings_text_entries:
            finding_text_ = FindingText(
                report_id=self.report_id,
                finding_ref_number=entry["reference_number"],
                contains_chart_or_table=entry["contains_chart_or_table"] == "Y",
                finding_text=entry["text_of_finding"],
            )
            findings_text_objects.append(finding_text_)
        self.loaded_objects["FindingTexts"] = findings_text_objects
        return findings_text_objects

    def load_findings(self):
        findings_objects = []
        findings_uniform_guidance = (
            self.single_audit_checklist.findings_uniform_guidance
        )

        if findings_uniform_guidance:
            findings_uniform_guidance_entries = findings_uniform_guidance.get(
                "FindingsUniformGuidance", {}
            ).get("findings_uniform_guidance_entries", [])
            
            for entry in findings_uniform_guidance_entries:
                findings = entry["findings"]
                program = entry["program"]

                finding = Finding(
                    award_reference=program["award_reference"],
                    reference_number=findings["reference_number"],
                    is_material_weakness=entry["material_weakness"],
                    is_modified_opinion=entry["modified_opinion"],
                    is_other_findings=entry["other_findings"],
                    is_other_matters=entry["other_matters"],
                    is_questioned_costs=entry["questioned_costs"],
                    is_repeat_finding=findings["repeat_prior_reference"],
                    is_significant_deficiency=entry["significant_deficiency"],
                    prior_finding_ref_numbers=findings.get("prior_references", ""),
                    report_id=self.report_id,
                    type_requirement=program["compliance_requirement"],
                )
                findings_objects.append(finding)

        self.loaded_objects["Findings"] = findings_objects
        return findings_objects

    def conditional_lookup(self, dict, key, default):
        if key in dict:
            return dict[key]
        else:
            return default

    def load_federal_award(self):
        federal_awards = self.single_audit_checklist.federal_awards
        federal_awards_objects = []

        for entry in federal_awards["FederalAwards"]["federal_awards"]:
            program = entry["program"]
            loan = entry["loan_or_loan_guarantee"]
            cluster = entry["cluster"]
            federal_award = FederalAward(
                additional_award_identification=program.get(
                    "additional_award_identification", ""
                ),
                amount_expended=program["amount_expended"],
                award_reference=entry["award_reference"],
                cluster_name=cluster["cluster_name"],
                cluster_total=cluster["cluster_total"],
                federal_agency_prefix=program["federal_agency_prefix"],
                federal_award_extension=program["three_digit_extension"],
                federal_program_name=program["program_name"],
                federal_program_total=program["federal_program_total"],
                findings_count=program["number_of_audit_findings"],
                is_direct=entry["direct_or_indirect_award"]["is_direct"],
                is_loan=loan["is_guaranteed"],
                is_major=program["is_major"],
                is_passthrough_award=entry["subrecipients"]["is_passed"],
                loan_balance=loan.get("loan_balance_at_audit_period_end", ""),
                audit_report_type=program.get("audit_report_type", ""),
                other_cluster_name=cluster.get("other_cluster_name", ""),
                # If the user entered "N" for is_passthrough_award, there will be no value for `passthrough_amount`.
                # We insert a `null`, as opposed to a 0, in that case.
                passthrough_amount=entry["subrecipients"].get(
                    "subrecipient_amount", None
                ),
                report_id=self.single_audit_checklist.report_id,
                state_cluster_name=cluster.get("state_cluster_name", ""),
            )
            federal_awards_objects.append(federal_award)
        self.loaded_objects["FederalAwards"] = federal_awards_objects
        return federal_awards_objects

    def load_captext(self):
        cap_text_objects = []
        corrective_action_plan = self.single_audit_checklist.corrective_action_plan

        if corrective_action_plan:
            corrective_action_plan_entries = corrective_action_plan.get(
                "CorrectiveActionPlan", {}
            ).get("corrective_action_plan_entries", [])
            
            for entry in corrective_action_plan_entries:
                cap_text = CapText(
                    contains_chart_or_table=entry["contains_chart_or_table"],
                    finding_ref_number=entry["reference_number"],
                    planned_action=entry["planned_action"],
                    report_id=self.report_id,
                )
                cap_text_objects.append(cap_text)

        self.loaded_objects["CapTexts"] = cap_text_objects
        return cap_text_objects

    def load_notes(self):
        sefa = self.single_audit_checklist.notes_to_sefa
        n2sefa = sefa.get("NotesToSefa", {})
        sefa_objects = []
        if n2sefa:
            accounting_policies = n2sefa["accounting_policies"]
            is_minimis_rate_used = n2sefa["is_minimis_rate_used"]
            rate_explained = n2sefa["rate_explained"]
            entries = n2sefa.get("notes_to_sefa_entries", [])
            if len(entries) == 0:
                note = Note(
                    report_id=self.report_id,
                    accounting_policies=accounting_policies,
                    is_minimis_rate_used=is_minimis_rate_used,
                    rate_explained=rate_explained,
                )
                sefa_objects.append(note)
            else:
                for entry in entries:
                    note = Note(
                        report_id=self.report_id,
                        accounting_policies=accounting_policies,
                        is_minimis_rate_used=is_minimis_rate_used,
                        rate_explained=rate_explained,
                        content=entry["note_content"],
                        note_title=entry["note_title"],
                    )
                    sefa_objects.append(note)
        self.loaded_objects["Notes"] = sefa_objects
        return sefa_objects

    def load_passthrough(self):
        federal_awards = self.single_audit_checklist.federal_awards
        federal_awards_entries = federal_awards.get("FederalAwards", {}).get(
            "federal_awards", []
        )
        pass_objects = []
        for entry in federal_awards_entries:
            entities = entry.get("direct_or_indirect_award", {}).get("entities", [])
            for entity in entities:
                passthrough = Passthrough(
                    award_reference=entry["award_reference"],
                    report_id=self.report_id,
                    passthrough_id=entity.get("passthrough_identifying_number", ""),
                    passthrough_name=entity["passthrough_name"],
                )
                pass_objects.append(passthrough)
        self.loaded_objects["Passthroughs"] = pass_objects
        return pass_objects

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

    def _bool_to_yes_no(self, condition):
        return "Yes" if condition else "No"

    def _optional_bool(self, condition):
        if condition is None:
            return ""
        else:
            return "Yes" if condition else "No"

    def _json_array_to_str(self, json_array):
        if json_array is None:
            return ""
        elif isinstance(json_array, list):
            return ", ".join(map(str, json_array))
        else:
            # FIXME This should raise an error
            return f"NOT AN ARRAY: {json_array}"

    def load_general(self):
        general_information = self.single_audit_checklist.general_information
        auditee_certification = self.single_audit_checklist.auditee_certification
        audit_information = self.single_audit_checklist.audit_information
        # auditor_certification = self.single_audit_checklist.auditor_certification

        dates_by_status = self._get_dates_from_sac()

        general = General(
            report_id=self.report_id,
            auditee_certify_name=auditee_certification["auditee_signature"][
                "auditee_name"
            ],
            auditee_certify_title=auditee_certification["auditee_signature"][
                "auditee_title"
            ],
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
            is_additional_ueis=self._bool_to_yes_no(
                general_information["multiple_ueis_covered"]
            ),
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
            auditor_foreign_address=general_information.get(
                "auditor_international_address", ""
            ),
            auditor_ein=general_information["auditor_ein"],
            cognizant_agency=self.single_audit_checklist.cognizant_agency
            if self.single_audit_checklist.cognizant_agency
            else "",
            oversight_agency=self.single_audit_checklist.oversight_agency
            if self.single_audit_checklist.oversight_agency
            else "",
            date_created=self.single_audit_checklist.date_created,
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
            # auditor_signature_date=auditor_certification["auditor_signature"]["auditor_certification_date_signed"],
            # auditee_signature_date=auditee_certification["auditee_signature"]["auditee_certification_date_signed"],
            fy_end_date=general_information["auditee_fiscal_period_end"],
            fy_start_date=general_information["auditee_fiscal_period_start"],
            audit_year=str(self.audit_year),
            audit_type=general_information["audit_type"],
            gaap_results=self._json_array_to_str(audit_information["gaap_results"]),
            sp_framework_basis=self._json_array_to_str(
                audit_information.get("sp_framework_basis")
            ),
            is_sp_framework_required=self._optional_bool(
                audit_information.get("is_sp_framework_required", None)
            ),
            sp_framework_opinions=self._json_array_to_str(
                audit_information.get("sp_framework_opinions")
            ),
            is_going_concern_included=self._bool_to_yes_no(
                audit_information["is_going_concern_included"]
            ),
            is_internal_control_deficiency_disclosed=self._bool_to_yes_no(
                audit_information["is_internal_control_deficiency_disclosed"]
            ),
            is_internal_control_material_weakness_disclosed=self._bool_to_yes_no(
                audit_information["is_internal_control_material_weakness_disclosed"]
            ),
            is_material_noncompliance_disclosed=self._bool_to_yes_no(
                audit_information["is_material_noncompliance_disclosed"]
            ),
            # is_duplicate_reports = self._bool_to_yes_no(audit_information["is_aicpa_audit_guide_included"]), #FIXME This mapping does not seem correct
            is_aicpa_audit_guide_included=self._bool_to_yes_no(
                audit_information["is_aicpa_audit_guide_included"]
            ),
            dollar_threshold=audit_information["dollar_threshold"],
            is_low_risk_auditee=self._bool_to_yes_no(
                audit_information["is_low_risk_auditee"]
            ),
            agencies_with_prior_findings=self._json_array_to_str(
                audit_information["agencies"]
            ),
            entity_type=general_information["user_provided_organization_type"],
            number_months=general_information.get("audit_period_other_months", ""),
            audit_period_covered=general_information["audit_period_covered"],
            total_amount_expended=self.single_audit_checklist.federal_awards[
                "FederalAwards"
            ]["total_amount_expended"],
            type_audit_code="UG",
            is_public=self.single_audit_checklist.is_public,
            data_source=self.single_audit_checklist.data_source,
        )

        self.loaded_objects["Generals"] = [general]
        return [general]

    def load_secondary_auditor(self):
        sec_objs = []
        secondary_auditors = self.single_audit_checklist.secondary_auditors

        if secondary_auditors:
            secondary_auditors_entries = secondary_auditors.get(
                "SecondaryAuditors", {}
            ).get("secondary_auditors_entries", [])
            
            for secondary_auditor in secondary_auditors_entries:
                sec_auditor = SecondaryAuditor(
                    address_city=secondary_auditor["secondary_auditor_address_city"],
                    address_state=secondary_auditor["secondary_auditor_address_state"],
                    address_street=secondary_auditor["secondary_auditor_address_street"],
                    address_zipcode=secondary_auditor["secondary_auditor_address_zipcode"],
                    auditor_ein=secondary_auditor["secondary_auditor_ein"],
                    auditor_name=secondary_auditor["secondary_auditor_name"],
                    contact_email=secondary_auditor["secondary_auditor_contact_email"],
                    contact_name=secondary_auditor["secondary_auditor_contact_name"],
                    contact_phone=secondary_auditor["secondary_auditor_contact_phone"],
                    contact_title=secondary_auditor["secondary_auditor_contact_title"],
                    report_id=self.single_audit_checklist.report_id,
                )
                sec_objs.append(sec_auditor)

        self.loaded_objects["SecondaryAuditors"] = sec_objs
        return sec_objs

    def load_additional_ueis(self):
        addls = self.single_audit_checklist.additional_ueis
        if (
            addls
            and "AdditionalUEIs" in addls
            and "additional_ueis_entries" in addls["AdditionalUEIs"]
        ):
            for uei in addls["AdditionalUEIs"]["additional_ueis_entries"]:
                auei = AdditionalUei(
                    report_id=self.single_audit_checklist.report_id,
                    additional_uei=uei["additional_uei"],
                )
                auei.save()  # FIXME: We could use a bulk insert here. Also, we could do all save in a batch.
