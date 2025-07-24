from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
)
from django.core.management.base import BaseCommand
from audit.models.constants import STATUS
from dissemination.models.general import ResubmissionStatus

from datetime import datetime
import pytz
import os

import logging
import sys
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SAC_WITH_DIFFERENT_PDF = {"report_id": "2019-06-CENSUS-0000191689"}

User = get_user_model()
from audit.models.submission_event import SubmissionEvent


#############################################
# modify_total_amount_expended
#############################################
def modify_total_amount_expended(sac):
    logger.info("MODIFIER: modify_total_amount_expended")
    current_amount = sac.federal_awards["FederalAwards"]["total_amount_expended"]
    new_amount = current_amount - 100000
    sac.federal_awards["FederalAwards"]["total_amount_expended"] = new_amount


#############################################
# modify_auditee_ein
#############################################
def modify_auditee_ein(sac):
    logger.info("MODIFIER: modify_auditee_ein")
    sac.general_information["ein"] = "999888777"


#############################################
# modify_auditor_address
#############################################
def modify_auditor_address(sac):
    """
    Modify a resubmission with a new address
    """
    logger.info("MODIFIER: modify_address")
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


#############################################
# modify_additional_eins_workbook
#############################################
def modify_additional_eins_workbook(sac):
    """
    Modify a resubmission with a changed workbook
    """
    logger.info("MODIFIER: modify_workbook")
    sac.additional_eins["AdditionalEINs"]["additional_eins_entries"].append(
        {"additional_ein": "111222333"},
    )


#############################################
# modify_pdf_point_at_this_instead
#############################################
def modify_pdf_point_at_this_instead(report_id):
    """
    Modify a resubmission with a changed PDF
    This function returns a function (breaking the pattern)
    so we can pass in a report id for the PDF that we want to *point to*.
    """

    def _do_modify(sac):
        logger.info("MODIFIER: modify_pdf")
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        sar = SingleAuditReportFile.objects.get(sac=sac)

        sar.sac_id = sac.id
        # TODO: This also causes a LateChangeError
        sar.save(
            administrative_override=True,
            event_user=User.objects.first(),
            event_type="bogus-event-generate-test-pdf",
        )

    return _do_modify


REPORTIDS_TO_MODIFIERS = lambda: {
    # Lets rewrite the auditor's address
    "2023-01-GSAFAC-0000000854": [modify_auditor_address],
    "2019-12-CENSUS-0000230175": [modify_auditee_ein],
    # Modifying the workbook requires there to be additional EINs
    "2023-06-GSAFAC-0000008301": [modify_additional_eins_workbook],
    "2023-12-GSAFAC-0000027107": [
        modify_auditor_address,
        modify_additional_eins_workbook,
    ],
    # modify_pdf simulates a new PDF submission.
    # The report on the left has its SAR pointer modified so that it instead
    # points to the report for the entity on the right. That way,
    # it looks like a completely different PDF is attached to (say) 19157.
    "2023-06-GSAFAC-0000019157": [
        modify_pdf_point_at_this_instead("2019-06-CENSUS-0000191689")
    ],
    "2023-06-GSAFAC-0000001699": [modify_total_amount_expended],
    # Do all the things
    "2023-06-GSAFAC-0000003056": [
        modify_auditor_address,
        modify_auditee_ein,
        modify_additional_eins_workbook,
        modify_total_amount_expended,
        modify_pdf_point_at_this_instead("2023-05-GSAFAC-0000000499"),
    ],
}


def complete_resubmission(
    source_sac: SingleAuditChecklist, resubmitted_sac: SingleAuditChecklist, USER_OBJ
):
    # The new SAC wants to be shifted to a disseminated state.
    resubmitted_sac.transition_name.append(STATUS.DISSEMINATED)
    resubmitted_sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    resubmitted_sac.submission_status = STATUS.DISSEMINATED
    resubmitted_sac.submitted_by = USER_OBJ
    resubmitted_sac.save(
        administrative_override=True,
        event_user=USER_OBJ,
        event_type="bogus-event-generate-test-data",
    )

    # We need to add some metadata to the original record, pointing to the resubmitted record.
    new_version = resubmitted_sac.resubmission_meta["version"]
    prev_version = new_version - 1
    source_meta = source_sac.resubmission_meta or {}
    source_sac.resubmission_meta = source_meta | {
        "next_report_id": resubmitted_sac.report_id,
        "next_row_id": resubmitted_sac.id,
        "version": prev_version,
        "resubmission_status": ResubmissionStatus.DEPRECATED,
    }
    # The original SAC needs to have its status set to "RESUBMITTED"
    source_sac.transition_name.append(STATUS.RESUBMITTED)
    source_sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    source_sac.save(
        administrative_override=True,
        event_user=USER_OBJ,
        event_type="bogus-event-finalize-resubmission-test-data",
    )

    # Finally, redisseminate the old and new SAC records.
    new_status = source_sac.redisseminate()
    old_status = resubmitted_sac.redisseminate()
    return old_status and new_status


class Command(BaseCommand):
    """
    Django management command for generating resubmission test data. Only run
    after using menu.bash to truncate tables and loading a base set of data.
    This selectively modifies specific reports so they are resubmitted, and then
    modifies the data of the resubmitted reports so we can test if there were changes.
    """

    def handle(self, *args, **options):
        reportids_to_modifiers = REPORTIDS_TO_MODIFIERS()

        sacs_for_resubs = SingleAuditChecklist.objects.filter(
            report_id__in=reportids_to_modifiers.keys()
        )
        if len(sacs_for_resubs) != len(reportids_to_modifiers.keys()):
            logger.error(
                f"Expected {len(reportids_to_modifiers.keys())} SACs, found {len(sacs_for_resubs)}. Make sure to truncate and load tables via menu.bash first."
            )
            sys.exit(1)

        # Delete any prior resubmissions, so we regenerate this data clean each time.
        for sac in sacs_for_resubs:
            for resub in SingleAuditChecklist.objects.filter(
                resubmission_meta__previous_report_id=sac.report_id
            ):
                logger.info(f"Deleting {resub.report_id}, a resub of {sac.report_id}")
                resub.delete()

        for sac in sacs_for_resubs:
            logger.info("-------------------------------")
            logger.info(f"Generating resubmission for {sac.report_id}")
            self.generate_resubmission(
                sac, options, reportids_to_modifiers[sac.report_id]
            )

    def generate_resubmission(self, sac: SingleAuditChecklist, options, modifiers):

        # We need a user.
        # FIXME: Allow an email address to be passed in, so we can see these things
        # in our dashboards. For now: any user will do.
        try:
            THE_USER_OBJ = User.objects.get(email=os.getenv("RESUBMISSION_EMAIL"))
        except:
            THE_USER_OBJ = User.objects.first()
        logger.info(
            f"Using user {os.getenv('RESUBMISSION_EMAIL')} {THE_USER_OBJ.email}"
        )

        # Start by taking a record and duplicating it, save for
        # some of the state around the transitions.
        new_sac = sac.initiate_resubmission(user=THE_USER_OBJ)

        logger.info(f"New SAC: {new_sac.report_id}")
        logger.info(f"Created new SAC with ID: {new_sac.id}")

        # Get the PDF report associated with this SAC, and
        # create a "resubmitted" PDF
        sac_sar = SingleAuditReportFile.objects.filter(sac=sac).first()
        sac_sar.file.name = f"singleauditreport/{new_sac.report_id}.pdf"
        new_sac_sar = SingleAuditReportFile.objects.create(
            file=sac_sar.file,
            sac=new_sac,
            audit=sac_sar.audit,  # We're not bothering to make a new audit
            user=sac_sar.user,
            component_page_numbers=sac_sar.component_page_numbers,
        )
        logger.info(f"Created new SAR with ID: {new_sac_sar.id}")

        # Perform modifications on the new resubmission
        # Invokes one or more modification functions (below)
        for modification in modifiers:
            modification(new_sac)

        # Make sure we created a valid SAC entry.
        # If not, error out.
        errors = new_sac.validate_full()
        if errors:
            logger.error(
                f"Unable to disseminate report with validation errors: {new_sac.report_id}."
            )
            logger.info(errors["errors"])

        # If we're here, we make sure the new SAC (which is a resubmission)
        # has all the right data/fields to be used for resubmission testing.
        # Need to be in the disseminated state in order to re-disseminated
        disseminated = complete_resubmission(sac, new_sac, THE_USER_OBJ)

        if disseminated:
            # TODO: Change submission_status to disseminated once Matt's
            # "late change" workaround is merged
            logger.info(f"DISSEMINATED REPORT: {new_sac.report_id}")
        else:
            logger.error(
                "{} is a `not None` value report_id[{}] for `disseminated`".format(
                    disseminated, new_sac.report_id
                )
            )
