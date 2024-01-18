import logging
import pytz
from django.db import IntegrityError

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
    AdditionalEin,
)
from audit.utils import Util

logger = logging.getLogger(__name__)


def omit(remove, d) -> dict:
    """omit(["a"], {"a":1, "b": 2}) => {"b": 2}"""
    return {k: d[k] for k in d if k not in remove}


class IntakeToDissemination(object):
    DISSEMINATION = "dissemination"
    PRE_CERTIFICATION_REVIEW = "pre_certification_review"

    def __init__(self, sac, mode=DISSEMINATION) -> None:
        self.single_audit_checklist = sac
        self.report_id = sac.report_id
        audit_date = sac.general_information["auditee_fiscal_period_end"]
        self.audit_year = int(audit_date.split("-")[0])
        self.loaded_objects: dict[str, list] = {}
        self.mode = mode

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
            "AdditionalEINs": self.load_additional_eins,
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
        for key, object_list in self.loaded_objects.items():
            try:
                if object_list:
                    model_class = type(object_list[0])
                    model_class.objects.bulk_create(object_list)
            except IntegrityError as e:
                logging.warning(
                    f"An error occurred during bulk creation for {key}: {e}"
                )

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text

        findings_text_objects = []
        if findings_text:
            findings_text_entries = findings_text.get("FindingsText", {}).get(
                "findings_text_entries", []
            )
            for entry in findings_text_entries:
                finding_text_ = FindingText(
                    report_id=self.report_id,
                    finding_ref_number=entry["reference_number"],
                    contains_chart_or_table=entry["contains_chart_or_table"],
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
        """
        Transforms the notes_to_sefa contents into the structure required for
        dissemination. This structure is a list of dissemination.models.Note instances.
        """
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
                        contains_chart_or_table=entry["contains_chart_or_table"],
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

    def _convert_utc_to_american_samoa_zone(self, date):
        us_samoa_zone = pytz.timezone("US/Samoa")
        # Ensure the datetime object is time zone aware
        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
            date = pytz.utc.localize(date)
        # Convert to American Samoa timezone (UTC-11)
        american_samoa_time = date.astimezone(us_samoa_zone)
        # Extract the date and format it as YYYY-MM-DD
        formatted_date = american_samoa_time.strftime("%Y-%m-%d")

        return formatted_date

    def load_general(self):
        """
        Transforms general_information and other content into the structure required for
        dissemination. This structure is a list with one entry, a
        dissemination.models.General instance.
        """
        general_information = self.single_audit_checklist.general_information
        audit_information = self.single_audit_checklist.audit_information
        auditee_certification = self.single_audit_checklist.auditee_certification
        auditor_certification = self.single_audit_checklist.auditor_certification or {}
        tribal_data_consent = self.single_audit_checklist.tribal_data_consent or {}
        cognizant_agency = self.single_audit_checklist.cognizant_agency
        oversight_agency = self.single_audit_checklist.oversight_agency

        dates_by_status = self._get_dates_from_sac()
        status = self.single_audit_checklist.STATUS
        ready_for_certification_date = dates_by_status[status.READY_FOR_CERTIFICATION]
        if self.mode == IntakeToDissemination.DISSEMINATION:
            submitted_date = self._convert_utc_to_american_samoa_zone(
                dates_by_status[status.SUBMITTED]
            )
            fac_accepted_date = submitted_date
            auditee_certify_name = auditee_certification["auditee_signature"][
                "auditee_name"
            ]
            auditee_certify_title = auditee_certification["auditee_signature"][
                "auditee_title"
            ]
            auditor_certify_name = auditor_certification["auditor_signature"][
                "auditor_name"
            ]
            auditor_certify_title = auditor_certification["auditor_signature"][
                "auditor_title"
            ]
            auditor_certified_date = dates_by_status[status.AUDITOR_CERTIFIED]
            auditee_certified_date = dates_by_status[status.AUDITEE_CERTIFIED]
        elif self.mode == IntakeToDissemination.PRE_CERTIFICATION_REVIEW:
            submitted_date = None
            fac_accepted_date = submitted_date
            auditee_certify_name = None
            auditee_certify_title = None
            auditee_certified_date = None
            auditor_certify_name = None
            auditor_certify_title = None
            auditor_certified_date = None

        total_amount_expended = self.single_audit_checklist.federal_awards[
            "FederalAwards"
        ]["total_amount_expended"]

        # Some keys in sac.general_information are different or absent in General
        gen_key_exceptions = (
            # Handled below:
            "audit_period_other_months",
            "auditee_fiscal_period_end",
            "auditee_fiscal_period_start",
            "auditor_international_address",
            "ein",
            "multiple_ueis_covered",
            "user_provided_organization_type",
            # Omitted:
            "auditor_ein_not_an_ssn_attestation",
            "ein_not_an_ssn_attestation",
            "is_usa_based",
            "met_spending_threshold",
            "multiple_eins_covered",
            "secondary_auditors_exist",
        )
        general_data = omit(gen_key_exceptions, general_information)
        general_data = general_data | {
            "number_months": general_information.get("audit_period_other_months", ""),
            "fy_end_date": general_information["auditee_fiscal_period_end"],
            "fy_start_date": general_information["auditee_fiscal_period_start"],
            "auditor_foreign_address": general_information.get(
                "auditor_international_address", ""
            ),
            "auditee_ein": general_information["ein"],
            "entity_type": general_information["user_provided_organization_type"],
        }
        if "multiple_ueis_covered" in general_information:
            addl = Util.bool_to_yes_no(general_information["multiple_ueis_covered"])
            general_data["is_additional_ueis"] = addl

        if general_information["user_provided_organization_type"] == "tribal":
            is_public = tribal_data_consent[
                "is_tribal_information_authorized_to_be_public"
            ]
        else:
            is_public = True

        # Various values in audit_information need special handling
        audit_data = {
            "agencies_with_prior_findings": Util.json_array_to_str(
                audit_information["agencies"]
            ),
            "dollar_threshold": audit_information["dollar_threshold"],
            "gaap_results": Util.json_array_to_str(audit_information["gaap_results"]),
        }
        audit_keys_arrtostr_opt = (
            "sp_framework_basis",
            "sp_framework_opinions",
        )
        audit_keys_yn = (
            "is_going_concern_included",
            "is_internal_control_deficiency_disclosed",
            "is_internal_control_material_weakness_disclosed",
            "is_material_noncompliance_disclosed",
            "is_aicpa_audit_guide_included",
            "is_low_risk_auditee",
        )
        audit_keys_opt_bool = ("is_sp_framework_required",)
        for key in audit_keys_arrtostr_opt:
            audit_data[key] = Util.json_array_to_str(audit_information.get(key))
        for key in audit_keys_yn:
            audit_data[key] = Util.bool_to_yes_no(audit_information[key])
        for key in audit_keys_opt_bool:
            audit_data[key] = Util.optional_bool(audit_information.get(key, None))

        general = General(
            report_id=self.report_id,
            auditee_certify_name=auditee_certify_name,
            auditee_certify_title=auditee_certify_title,
            auditor_certify_name=auditor_certify_name,
            auditor_certify_title=auditor_certify_title,
            cognizant_agency=cognizant_agency,
            oversight_agency=oversight_agency,
            date_created=self.single_audit_checklist.date_created,
            ready_for_certification_date=ready_for_certification_date,
            auditor_certified_date=auditor_certified_date,
            auditee_certified_date=auditee_certified_date,
            submitted_date=submitted_date,
            fac_accepted_date=fac_accepted_date,
            audit_year=str(self.audit_year),
            total_amount_expended=total_amount_expended,
            type_audit_code="UG",
            is_public=is_public,
            data_source=self.single_audit_checklist.data_source,
            **general_data,
            **audit_data,
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
                    address_street=secondary_auditor[
                        "secondary_auditor_address_street"
                    ],
                    address_zipcode=secondary_auditor[
                        "secondary_auditor_address_zipcode"
                    ],
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
        uei_objs = []
        if (
            addls
            and "AdditionalUEIs" in addls
            and "additional_ueis_entries" in addls["AdditionalUEIs"]
        ):
            for entry in addls["AdditionalUEIs"]["additional_ueis_entries"]:
                uei = AdditionalUei(
                    report_id=self.single_audit_checklist.report_id,
                    additional_uei=entry["additional_uei"],
                )
                uei_objs.append(uei)
        self.loaded_objects["AdditionalUEIs"] = uei_objs
        return uei_objs

    def load_additional_eins(self):
        addls = self.single_audit_checklist.additional_eins
        ein_objs = []
        if (
            addls
            and "AdditionalEINs" in addls
            and "additional_eins_entries" in addls["AdditionalEINs"]
        ):
            for entry in addls["AdditionalEINs"]["additional_eins_entries"]:
                ein = AdditionalEin(
                    report_id=self.single_audit_checklist.report_id,
                    additional_ein=entry["additional_ein"],
                )
                ein_objs.append(ein)
        self.loaded_objects["AdditionalEINs"] = ein_objs
        return ein_objs
