from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
)
from django.core.management.base import BaseCommand
from audit.models.constants import STATUS, RESUBMISSION_STATUS
from audit.cross_validation.naming import SECTION_NAMES

from datetime import datetime
import pytz

import logging
import sys
from django.contrib.auth import get_user_model

from copy import deepcopy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


# Using the new tools to generate data for local testing,
# we want to make sure these are selected from our
# 20K record subset, so that the command always works.
REPORTIDS_TO_MODIFIERS = lambda: {
    # Lets rewrite the auditor's address
    "2023-06-GSAFAC-0000000697": [modify_auditor_address],
    "2023-06-GSAFAC-0000002166": [modify_auditee_ein],
    # Modifying the workbook requires there to be additional EINs
    "2022-12-GSAFAC-0000001787": [modify_additional_eins_workbook],
    "2023-06-GSAFAC-0000002901": [
        modify_auditor_address,
        modify_additional_eins_workbook,
    ],
    # Same modifications as above, but will make a new resub for each
    # See REPORTIDS_TO_RESUBMIT_MODIFIERS_SEPARATELY below
    "2023-06-GSAFAC-0000013043": [
        modify_auditor_address,
        modify_additional_eins_workbook,
    ],
    # modify_pdf simulates a new PDF submission.
    # The report on the left has its SAR pointer modified so that it instead
    # points to the report for the entity on the right. That way,
    # it looks like a completely different PDF is attached to (say) 19157.
    "2023-06-GSAFAC-0000005147": [
        modify_pdf_point_at_this_instead("2023-06-GSAFAC-0000002901")
    ],
    "2023-06-GSAFAC-0000001699": [modify_total_amount_expended],
    # Do all the things
    "2022-12-GSAFAC-0000007921": [
        modify_auditor_address,
        modify_auditee_ein,
        modify_additional_eins_workbook,
        modify_total_amount_expended,
        modify_pdf_point_at_this_instead("2023-06-GSAFAC-0000000697"),
    ],
}

REPORTIDS_TO_RESUBMIT_MODIFIERS_SEPARATELY = ["2023-06-GSAFAC-0000013043"]


#############################################
# modify_total_amount_expended
#############################################
def modify_total_amount_expended(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: modify_total_amount_expended")
    new_sac.federal_awards = deepcopy(old_sac.federal_awards)
    current_amount = old_sac.federal_awards["FederalAwards"]["total_amount_expended"]
    new_amount = current_amount - 100000
    new_sac.federal_awards["FederalAwards"]["total_amount_expended"] = new_amount
    return new_sac


#############################################
# modify_auditee_ein
#############################################
def modify_auditee_ein(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: modify_auditee_ein")
    new_sac.general_information = deepcopy(old_sac.general_information)
    new_sac.general_information["ein"] = "999888777"
    return new_sac


#############################################
# modify_auditor_address
#############################################
def modify_auditor_address(old_sac, new_sac, user_obj):
    """
    Modify a resubmission with a new address
    """
    logger.info("MODIFIER: modify_address")
    new_sac.general_information = deepcopy(old_sac.general_information)
    new_sac.general_information["auditor_address_line_1"] = "123 Across the street"
    new_sac.general_information["auditor_zip"] = "17921"
    new_sac.general_information["auditor_city"] = "Centralia"
    new_sac.general_information["auditor_state"] = "PA"
    new_sac.general_information["auditor_phone"] = "7777777777"
    new_sac.general_information["auditor_contact_name"] = "Jill Doe"
    new_sac.general_information["auditor_firm_name"] = "Other House of Auditor"
    new_sac.general_information["auditor_email"] = (
        "other.qualified.human.accountant@auditor.com"
    )
    return new_sac


#############################################
# modify_additional_eins_workbook
#############################################
def modify_additional_eins_workbook(old_sac, new_sac, user_obj):
    """
    Modify a resubmission with a changed workbook
    """
    logger.info("MODIFIER: modify_eins_workbook")
    if not new_sac.additional_eins or old_sac.additional_eins:
        logger.info(f"AUDIT {old_sac.report_id} HAS NO ADDITIONAL EINS TO MODIFY")
        logger.info("Fakin' it till I make it.")
        new_sac.additional_eins = {
            "Meta": {"section_name": "AdditionalEins"},
            "AdditionalEINs": {
                "auditee_uei": old_sac.auditee_uei,
                "additional_eins_entries": [],
            },
        }
    new_sac.additional_eins["AdditionalEINs"]["additional_eins_entries"].append(
        {"additional_ein": "111222333"},
    )
    return new_sac


#############################################
# modify_pdf_point_at_this_instead
#############################################
def modify_pdf_point_at_this_instead(old_report_id):
    """
    Modify a resubmission with a changed PDF
    This function returns a function (breaking the pattern)
    so we can pass in a report id for the PDF that we want to *point to*.
    """

    def _do_modify(old_sac, new_sac, user_obj):
        logger.info("MODIFIER: modify_pdf")
        logger.info(
            f"old_report_id: {old_report_id} new_report_id: {new_sac.report_id}"
        )
        old_sac = SingleAuditChecklist.objects.get(report_id=old_report_id)

        # Now we have a new SAC, and it points to a report.
        # We also have the old SAC.
        # I want delete the SAR currently associated with the new_sac
        # Then, I want to copy the SAR associated with the old SAC
        # Then, I want that copy to refer back to the new sac.

        # First, delete the SAR(s) we created as a default part of this test data generator.
        recently_created_sars = SingleAuditReportFile.objects.filter(sac=new_sac)
        logger.info(f"Found new SARS: {len(recently_created_sars)}")
        recently_created_sars.delete()
        logger.info(f"After delete: {len(recently_created_sars)}")

        # Then, copy the SAR associated with the old SAC.
        old_sar = (
            SingleAuditReportFile.objects.filter(sac=old_sac)
            .order_by("date_created")
            .first()
        )
        logger.info(f"SAR we are copying ID: {old_sar.id}")
        old_filename = f"{old_sar.filename}"

        # Null out the PK, and it will create a new one that is a copy.
        old_sar.pk = None
        # Now, this is effectively a NEW sar
        new_sar = old_sar
        # Now, point the SAC id of the new SAR at the new SAC id.
        new_sar.sac_id = new_sac.id
        # Save it as a new row
        logger.info(f"Trying to update filename to {old_filename}")
        new_sar.save(
            administrative_override=True,
            filename_override=old_filename,
            event_user=user_obj,
            event_type="bogus-event-generate-test-pdf",
        )
        logger.info(f"Saved as id {new_sar.id}")
        return new_sac

    return _do_modify


def complete_resubmission(
    source_sac: SingleAuditChecklist, resubmitted_sac: SingleAuditChecklist, USER_OBJ
):
    # The new SAC wants to be shifted to a disseminated state.
    append_transition_names(resubmitted_sac)
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
        "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
    }

    # The original SAC needs to have its status set to "RESUBMITTED"
    source_sac.transition_name.append(STATUS.RESUBMITTED)
    source_sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))

    # Go ahead and reassign this SAC to us, so we might see it in the UI at some point.
    source_sac.submitted_by = USER_OBJ
    source_sac.save(
        administrative_override=True,
        event_user=USER_OBJ,
        event_type="bogus-event-finalize-resubmission-test-data",
    )

    # Finally, redisseminate the old and new SAC records.
    new_status = source_sac.redisseminate()
    old_status = resubmitted_sac.redisseminate()
    return old_status and new_status


def append_transition_names(sac: SingleAuditChecklist):
    """
    Given a SAC, append transition names and dates to bring it to "disseminated".
    """
    sac.transition_name.append(STATUS.AUDITEE_CERTIFIED)
    sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    sac.transition_name.append(STATUS.AUDITOR_CERTIFIED)
    sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    sac.transition_name.append(STATUS.READY_FOR_CERTIFICATION)
    sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    sac.transition_name.append(STATUS.SUBMITTED)
    sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))
    sac.transition_name.append(STATUS.DISSEMINATED)
    sac.transition_date.append(datetime.now().replace(tzinfo=pytz.utc))

    return sac


def delete_prior_resubs(sacs):
    """
    Delete any prior resubmissions, so we regenerate this data clean each time
    """
    for sac in sacs:
        resubs = SingleAuditChecklist.objects.filter(
            resubmission_meta__previous_report_id=sac.report_id
        )
        recursively_delete_resubs_for_sac(sac, resubs)


def recursively_delete_resubs_for_sac(sac, resubs):
    """
    Since resubmissions can have resubmissions, we have to keep digging
    down for SACs that have previous_report_ids
    """
    if not resubs:
        return

    for resub in resubs:
        re_resubs = SingleAuditChecklist.objects.filter(
            resubmission_meta__previous_report_id=resub.report_id
        )
        recursively_delete_resubs_for_sac(resub, re_resubs)

        logger.info(f"Deleting {resub.report_id}, a resub of {sac.report_id}")
        resub.delete()


def generate_resubmissions(sacs, reportids_to_modifiers, options):
    """
    Generates all the resubmissions
    """
    for sac in sacs:
        logger.info("-------------------------------")

        if sac.report_id in REPORTIDS_TO_RESUBMIT_MODIFIERS_SEPARATELY:
            logger.info(f"Generating resubmission chain for {sac.report_id}")
            previous_sac = sac
            for modifier in reportids_to_modifiers[sac.report_id]:
                new_sac = generate_resubmission(previous_sac, options, [modifier])
                previous_sac = new_sac
        else:
            logger.info(f"Generating resubmission for {sac.report_id}")
            generate_resubmission(sac, options, reportids_to_modifiers[sac.report_id])


def create_resubmitted_pdf(sac, new_sac):
    # Get the PDF report associated with this SAC, and
    # create a "resubmitted" PDF
    sac_sar = SingleAuditReportFile.objects.filter(sac=sac).first()
    sac_sar.filename = f"singleauditreport/{new_sac.report_id}.pdf"
    new_sac_sar = SingleAuditReportFile.objects.create(
        file=sac_sar.file,
        sac=new_sac,
        audit=sac_sar.audit,  # We're not bothering to make a new audit
        user=sac_sar.user,
        component_page_numbers=sac_sar.component_page_numbers,
    )
    logger.info(f"Created new SAR with ID: {new_sac_sar.id}")


# {"ein": "222474723", "audit_type": "single-audit", "auditee_uei": "HXC9E9MTFLB6", "auditee_zip": "06851", "auditor_ein": "060530830", "auditor_zip": "06473", "auditee_city": "Norwalk", "auditee_name": "Miss Laura M. Raymond Homes, Inc.", "auditor_city": "North Haven", "is_usa_based": true, "auditee_email": "scox@ehmchm.org", "auditee_phone": "2032304809", "auditee_state": "CT", "auditor_email": "mloso@sewardmonde.com", "auditor_phone": "2032489341", "auditor_state": "CT", "auditor_country": "USA", "auditor_firm_name": "Seward and Monde, CPAs", "audit_period_covered": "annual", "auditee_contact_name": "Sabine Cox", "auditor_contact_name": "Michele Loso Boisvert", "auditee_contact_title": "Accounting Director", "auditor_contact_title": "Partner", "multiple_eins_covered": false, "multiple_ueis_covered": false, "auditee_address_line_1": "290 Main Avenue", "auditor_address_line_1": "296 State Street", "met_spending_threshold": true, "secondary_auditors_exist": false, "audit_period_other_months": "", "auditee_fiscal_period_end": "2023-06-30", "ein_not_an_ssn_attestation": true, "auditee_fiscal_period_start": "2022-07-01", "auditor_international_address": "", "user_provided_organization_type": "non-profit", "auditor_ein_not_an_ssn_attestation": true}


def get_user_object(options):
    # We need a user.
    # FIXME: Allow an email address to be passed in, so we can see these things
    # in our dashboards. For now: any user will do.
    try:
        THE_USER_OBJ = User.objects.get(email=options["email"])
    except User.MultipleObjectsReturned:
        # Mangled local DB's may have duplicate users.
        THE_USER_OBJ = User.objects.filter(email=options["email"]).first()
    except User.DoesNotExist:
        THE_USER_OBJ = User.objects.first()
    logger.info(f"Passed email: {options['email']}, Using user {THE_USER_OBJ}")
    return THE_USER_OBJ


def copy_data_over(old_sac, new_sac):
    # This simulates the auditee/auditor completing the submission.
    # So, we'll copy everything over from the old to the new.
    # In a real submission, they'd have to upload stuff.
    sac_fields = SECTION_NAMES.keys()
    for field in sac_fields:
        if field not in ["single_audit_report"]:
            setattr(new_sac, field, getattr(old_sac, field))


def generate_resubmission(sac: SingleAuditChecklist, options, modifiers):
    """
    Generates a single resubmission
    """
    # Get a user. Preferably us.
    THE_USER_OBJ = get_user_object(options)

    # Start by taking a record and duplicating it, save for
    # some of the state around the transitions.
    new_sac = sac.initiate_resubmission(user=THE_USER_OBJ, duplicate_for_test=True)

    logger.info(f"New SAC: {new_sac.report_id}")
    logger.info(f"Created new SAC with ID: {new_sac.id}")

    # Copy a PDF and create a new SAR record for it.
    create_resubmitted_pdf(sac, new_sac)

    # Now, copy a lot of data over from the old to the new.
    # This is not how we would normally do it, but we get a lot of errors otherwise.
    copy_data_over(sac, new_sac)

    # Perform modifications on the new resubmission
    # Invokes one or more modification functions (below)
    for modification in modifiers:
        new_sac = modification(sac, new_sac, THE_USER_OBJ)

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
        return new_sac
    else:
        logger.error(
            "{} is a `not None` value report_id[{}] for `disseminated`".format(
                disseminated, new_sac.report_id
            )
        )


class Command(BaseCommand):
    """
    Django management command for generating resubmission test data. Only run
    after using menu.bash to truncate tables and loading a base set of data.
    This selectively modifies specific reports so they are resubmitted, and then
    modifies the data of the resubmitted reports so we can test if there were changes.
    """

    def add_arguments(self, parser):
        parser.add_argument("--email", required=False)

    def handle(self, *args, **options):
        reportids_to_modifiers = REPORTIDS_TO_MODIFIERS()
        logger.info("Modifying the following report IDs")
        for rid in reportids_to_modifiers:
            logger.info(f"\t{rid}")
        sacs_for_resubs = SingleAuditChecklist.objects.filter(
            report_id__in=reportids_to_modifiers.keys()
        )
        if len(sacs_for_resubs) != len(reportids_to_modifiers.keys()):
            logger.error(
                f"Expected {len(reportids_to_modifiers.keys())} SACs, found {len(sacs_for_resubs)}. Make sure to truncate and load tables via menu.bash first."
            )
            sys.exit(1)

        delete_prior_resubs(sacs_for_resubs)
        generate_resubmissions(sacs_for_resubs, reportids_to_modifiers, options)
