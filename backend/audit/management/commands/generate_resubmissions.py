from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
)
from django.core.management.base import BaseCommand

import logging
import sys


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for generating resubmission test data. Only run
    after using menu.bash to truncate tables and load
    use_with_generate_resubmissions.dump.
    """

    def handle(self, *args, **options):
        # Note: D7A4J33FUMJ1 is also in the dump, buy it's our
        # control/no-resubmission case
        ueis_to_modifiers = {
            "TCMPSMEX54P3": [self.modify_address],
            "LJL3QNRFCKA7": [self.modify_workbook],
            "JP7BM2J3BKT8": [self.modify_address, self.modify_workbook],
            "CN2SV2P5ZL82": [], # This is available in the dump for future modifications
        }

        sacs = SingleAuditChecklist.objects.filter(
            general_information__auditee_uei__in=ueis_to_modifiers.keys()
        )

        if len(sacs) == len(ueis_to_modifiers.keys()):
            for sac in sacs:
                self.generate_resubmission(sac, ueis_to_modifiers[sac.auditee_uei])
        else:
            logger.error(
                f"Expected {len(ueis_to_modifiers.keys())} SACs, found {len(sacs)}. Make sure to truncate and load tables via menu.bash first."
            )
            sys.exit(1)

    def generate_resubmission(self, sac, modifiers):
        new_sac = SingleAuditChecklist.objects.create(
            submitted_by=sac.submitted_by,
            general_information=sac.general_information,
            federal_awards=sac.federal_awards,
            findings_uniform_guidance=sac.findings_uniform_guidance,
            notes_to_sefa=sac.notes_to_sefa,
            findings_text=sac.findings_text,
            corrective_action_plan=sac.corrective_action_plan,
            secondary_auditors=sac.secondary_auditors,
            additional_ueis=sac.additional_ueis,
            additional_eins=sac.additional_eins,
            audit_information=sac.audit_information,
            auditee_certification=sac.auditee_certification,
            auditor_certification=sac.auditor_certification,
            tribal_data_consent=sac.tribal_data_consent,
            cognizant_agency=sac.cognizant_agency,
            oversight_agency=sac.oversight_agency,
            transition_name=sac.transition_name,
            transition_date=sac.transition_date,
            audit_type=sac.audit_type,
        )

        logger.info(f"Created new SAC with ID: {new_sac.id}")

        sac_sar = SingleAuditReportFile.objects.filter(sac=sac).first()
        sac_sar.file.name = f"singleauditreport/{new_sac.report_id}.pdf"
        new_sac_sar = SingleAuditReportFile.objects.create(
            file=sac_sar.file,
            sac=new_sac,
            audit=sac_sar.audit, # We're not bothering to make a new audit
            user=sac_sar.user,
            component_page_numbers=sac_sar.component_page_numbers,
        )

        logger.info(f"Created new SAR with ID: {new_sac_sar.id}")

        for modification in modifiers:
            modification(new_sac)

        errors = new_sac.validate_full()
        if errors:
            logger.error(
                f"Unable to disseminate report with validation errors: {new_sac.report_id}."
            )
            logger.info(errors["errors"])
        else:
            new_sac.save()

            disseminated = new_sac.disseminate()
            if disseminated is None:
                # TODO: Change submission_status to disseminated once Matt's
                # "late change" workaround is merged
                logger.info(f"DISSEMINATED REPORT: {new_sac.report_id}")
            else:
                logger.error(
                    "{} is a `not None` value report_id[{}] for `disseminated`".format(
                        disseminated, new_sac.report_id
                    )
                )

    def modify_address(self, sac):
        """
        Modify a resubmission with a new address
        """
        sac.general_information["auditor_address_line_1"] = "123 Across the street"
        sac.general_information["auditor_zip"] = "17921"
        sac.general_information["auditor_city"] = "Centralia"
        sac.general_information["auditor_state"] = "PA"
        sac.general_information["auditor_phone"] = "7777777777"
        sac.general_information["auditor_contact_name"] = "Jill Doe"
        sac.general_information["auditor_firm_name"] = "Other House of Auditor"
        sac.general_information["auditor_email"] = (
            "other.qualified.human.accountant@auditor.com"
        )

    def modify_workbook(self, sac):
        """
        Modify a resubmission with a changed workbook
        """
        sac.additional_eins["AdditionalEINs"]["additional_eins_entries"].append(
            {"additional_ein": "111222333"},
        )
