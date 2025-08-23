##########################################################################
# THIS SHOULD NEVER BE RUN IN PRODUCTION
##########################################################################
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

import boto3

# In case it is needed for S3 operations.
# from boto3.s3.transfer import S3Transfer
from django.conf import settings

from copy import deepcopy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()

from inspect import currentframe

import os, sys

if os.getenv("ENV") == "PRODUCTION":
    # https://en.wikipedia.org/wiki/Long-term_nuclear_waste_warning_messages
    logger.error("The danger is still present, in your time, as it was in ours.")
    logger.error("DO NOT RUN THIS IN PRODUCTION")
    sys.exit(-1)

# Using the new tools to generate data for local testing,
# we want to make sure these are selected from our
# 20K record subset, so that the command always works.
REPORTIDS_TO_MODIFIERS = lambda: {
    # Lets rewrite the auditor's address
    "2023-06-GSAFAC-0000000697": [
        modify_auditor_address,
        # These two files have no changes that are visible, but
        # the PDFs were generated at two different times. Invisible to the user.
        upload_pdfs("o-captain.pdf", "o-captain-2.pdf"),
    ],
    "2023-06-GSAFAC-0000002166": [
        modify_auditee_ein,
        # The second file contains an image; the second does not
        upload_pdfs("federalist.pdf", "federalist-2.pdf"),
    ],
    # Modifying the workbook requires there to be additional EINs
    "2022-12-GSAFAC-0000001787": [
        modify_additional_eins_workbook,
        add_an_award,
        # The second file had its XML metadata changed. Instead of
        # being created by Acrobat Distiller 6.0, the second
        # was created by Acrobat Distiller 9.0. Invisible to the user.
        upload_pdfs("permanent-markers.pdf", "permanent-markers-2.pdf"),
    ],
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
    # Because we randomly fake tribal audits, this is tricky.
    # We may need to intentionally set one in here, and then flip it.
    # "2019-06-GSAFAC-0000005301": [flip_tribal_consent_status],
}

REPORTIDS_TO_RESUBMIT_MODIFIERS_SEPARATELY = ["2023-06-GSAFAC-0000013043"]


#########################################################
# WARNING WARNING WARNING
#########################################################
#
# When copying records, we *must* be super-duper careful. That is really
# technical language for "hypervigilant."
#
# SACs are objects. Therefore, an assignment like
#
# new_sac = old_sac
#
# is a pointer assignment. The new_sac and the old_sac variables are now
# pointing to the exact same location in memory---the same object.
#
# We can get around this by creating a new SAC (we do). But, then,
# in this script, data is copied from the old SAC to the new.
#
# This is fine for constants that are interned by the interpreter: integers
# and strings that we put in the code. (E.g. x="hi" and y="hi" both point to
# the same string in memory.) This is not an issue for us at this time.
#
# It is an issue for elements in the SAC that are *lists*. For example
# everything inside of every workbook field.
#
# If we copy the `general_information` over like this:
#
# new_sac.general_information = old_sac.general_information
#
# We have just set a pointer in the new_sac object to a dictionary inside
# the old_sac object.
#
# I have *no idea* why the old_sac objects are saving in this script. But, the old_sac
# objects are being modified. So, I have sprinkled two things throughout the code:
#
# * APNE
# * deepcopy
#
# APNE is "assert_pointer_not_equal." It makes sure two variables are pointing
# at different things in memory. It throws an assertion---forcing an exit---if the pointers
# are the same. It correctly (?) skips ints and strings.
#
# deepcopy should be copying values and not pointers. However, I've seen it not work.
# So, you'll see places where I walk a dictionary, and copy the k/v pairs over
# the hard way... with a deepcopy on the value.
#
# No idea. It's all bonkers. It shouldn't be this hard to create a clone of a SAC, but it is.
# This will matter a great deal in the future if we're going to allow users to edit live records.
# We have to be very, very careful to make sure that we are not modifying the original record
# through some kind of pointer confusion.
#
# For all I know, something like this is at play: https://www.reddit.com/r/django/comments/14vq6s7/comment/jrdxttz
# There are times when a Django model will auto-save itself. So, that may have been happening to the old_sac
# somewhere in this code. I wouldn't know. But I do know that the original was changing.
#
# MCJ 20250822


def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno


# asert_pointer_not_equal
def APNE(a, b, loc=None):
    if id(a) == id(b):
        if isinstance(a, int) and isinstance(b, int) and a == b:
            # We don't assert for integers; they always have the same pointer.
            return
        elif isinstance(a, str) and isinstance(b, str) and a == b:
            # Same for strings and other builtin types.
            return
        elif isinstance(a, bool) and isinstance(b, bool) and a == b:
            return
        else:
            logger.info(f"POINTERS EQUAL: {id(a)}")
            logger.info(f"VALUE: {a}")
            if loc is not None:
                logger.info(f"LOCATION: {loc}")
    assert id(a) != id(b)


#############################################
# upload_pdfs
#############################################
# This uploads the orig to the old sac, and the second
# to the new sac. We need to stuff real PDFs into the
# S3/Minio bucket in order to compare them.
def upload_pdfs(orig_pdf, revised_pdf):
    def _fun(old_sac, new_sac, user_obj):
        logger.info("MODIFIER: upload_pdfs")
        APNE(old_sac, new_sac)

        orig_sar = (
            SingleAuditReportFile.objects.filter(sac=old_sac)
            .order_by("date_created")
            .first()
        )

        revised_sar = (
            SingleAuditReportFile.objects.filter(sac=new_sac)
            .order_by("date_created")
            .first()
        )

        # These SARs will provide the filenames that we upload *to*.
        # The filenames given are the filenames in the fixtures directory.
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        # In the event that the transfer mode doesn't work, this is another
        # way to do it.
        # transfer = S3Transfer(client)
        # transfer.upload_file('/tmp/myfile', 'bucket', 'key')

        fixture_1 = f"audit/fixtures/{orig_pdf}"
        with open(fixture_1, "rb") as file:
            logger.info(f"Uploading {fixture_1} to {orig_sar.filename}")
            client.upload_fileobj(
                file,
                settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
                f"singleauditreport/{orig_sar.filename}",
            )

        fixture_2 = f"audit/fixtures/{revised_pdf}"
        with open(fixture_2, "rb") as file:
            logger.info(f"Uploading {fixture_2} to {revised_sar.filename}")
            client.upload_fileobj(
                file,
                settings.AWS_PRIVATE_STORAGE_BUCKET_NAME,
                f"singleauditreport/{revised_sar.filename}",
            )

        return new_sac

    return _fun


#############################################
# flip_tribal_consent_status
#############################################
def flip_tribal_consent_status(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: flip_tribal_consent_status")
    APNE(old_sac, new_sac)
    new_sac.general_information["user_provided_organization_type"] = "tribal"
    new_sac.tribal_data_consent["is_tribal_information_authorized_to_be_public"] = True
    return new_sac


#############################################
# remove_an_award
#############################################
def remove_an_award(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: remove_an_award")
    APNE(old_sac, new_sac)
    new_sac.federal_awards["FederalAwards"]["federal_awards"] = new_sac.federal_awards[
        "FederalAwards"
    ]["federal_awards"][:-1]
    return new_sac


#############################################
# add_an_award
#############################################
def add_an_award(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: add_an_award")
    APNE(old_sac, new_sac)
    new_sac.federal_awards["FederalAwards"]["federal_awards"].append(
        deepcopy(new_sac.federal_awards["FederalAwards"]["federal_awards"][0])
    )
    new_sac.federal_awards["FederalAwards"]["federal_awards"][1][
        "award_reference"
    ] = "AWARD-0002"

    return new_sac


#############################################
# modify_total_amount_expended
#############################################
def modify_total_amount_expended(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: modify_total_amount_expended")
    APNE(old_sac, new_sac)
    current_amount = old_sac.federal_awards["FederalAwards"]["total_amount_expended"]
    new_amount = current_amount - 100000
    new_sac.federal_awards["FederalAwards"]["total_amount_expended"] = new_amount
    return new_sac


#############################################
# modify_auditee_ein
#############################################
def modify_auditee_ein(old_sac, new_sac, user_obj):
    logger.info("MODIFIER: modify_auditee_ein")
    APNE(old_sac, new_sac)
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
    APNE(old_sac, new_sac)
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
    APNE(old_sac, new_sac)
    if not old_sac.additional_eins:
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
        APNE(old_sac, new_sac)
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
    for old_sac in sacs:
        logger.info("-------------------------------")

        if old_sac.report_id in REPORTIDS_TO_RESUBMIT_MODIFIERS_SEPARATELY:
            logger.info(f"Generating resubmission chain for {old_sac.report_id}")
            previous_sac = deepcopy(old_sac)
            APNE(previous_sac, old_sac)
            for modifier in reportids_to_modifiers[old_sac.report_id]:
                new_sac = generate_resubmission(previous_sac, options, [modifier])
                previous_sac = deepcopy(new_sac)
                APNE(previous_sac, new_sac)
        else:
            logger.info(f"Generating resubmission for {old_sac.report_id}")
            generate_resubmission(
                old_sac, options, reportids_to_modifiers[old_sac.report_id]
            )


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
    logger.info("ACTION: copy_data_over")
    APNE(old_sac, new_sac)
    sac_fields = SECTION_NAMES.keys()
    for field in sac_fields:
        if field not in ["single_audit_report"]:
            # Don't clobber what was created when we initialized the audit resubmission.
            if field == "general_information":
                for k, v in old_sac.general_information.items():
                    if k not in [
                        "auditee_uei",
                        "auditee_fiscal_period_start",
                        "auditee_fiscal_period_end",
                    ]:
                        new_v = deepcopy(v)
                        APNE(new_v, v, loc=get_linenumber())
                        new_sac.general_information[k] = new_v

            else:
                # This is a convoluted way to copy the section objects.
                # deepcopy(section) is not working. It is carrying pointers forward.
                # So, I go through the section, copying the keys/values the hard way.
                # At every step, assert that pointers are not equal.
                # This literally fixed a bug in this script, where lists of entries in
                # workbook sections were *pointer* copies, and as a result, modifying the
                # new_sac was also modifying the old_sac.
                # What I don't understand is why the old_sac was saving to the DB...
                section = getattr(old_sac, field)
                if section is None:
                    # Should this be None, or dict()?
                    # IT SHOULD BE NONE. That will match the prior DB row.
                    setattr(new_sac, field, None)
                else:
                    d = dict()
                    for k, v in section.items():
                        new_v = deepcopy(v)
                        APNE(new_v, v, loc=get_linenumber())
                        d[k] = new_v
                    setattr(new_sac, field, d)
                    APNE(
                        getattr(new_sac, field),
                        getattr(old_sac, field),
                        loc=get_linenumber(),
                    )


def generate_resubmission(old_sac: SingleAuditChecklist, options, modifiers):  #
    """
    Generates a single resubmission
    """
    # Get a user. Preferably us.
    THE_USER_OBJ = get_user_object(options)

    # Start by taking a record and duplicating it, save for
    # some of the state around the transitions.
    new_sac = old_sac.initiate_resubmission(user=THE_USER_OBJ)
    APNE(old_sac, new_sac)

    logger.info(f"New SAC: {new_sac.report_id}")
    logger.info(f"Created new SAC with ID: {new_sac.id}")

    # Copy a PDF and create a new SAR record for it.
    create_resubmitted_pdf(old_sac, new_sac)
    APNE(old_sac, new_sac)

    # Now, copy a lot of data over from the old to the new.
    # This is not how we would normally do it, but we get a lot of errors otherwise.
    copy_data_over(old_sac, new_sac)
    APNE(old_sac, new_sac)

    # Perform modifications on the new resubmission
    # Invokes one or more modification functions (below)
    for modification in modifiers:
        new_sac = modification(old_sac, new_sac, THE_USER_OBJ)
    APNE(old_sac, new_sac)

    # Make sure we created a valid SAC entry.
    # If not, error out.
    errors = new_sac.validate_full()
    if errors:
        logger.error(
            f"Unable to disseminate report with validation errors: {new_sac.report_id}."
        )
        logger.info(errors["errors"])
    else:
        # If we're here, we make sure the new SAC (which is a resubmission)
        # has all the right data/fields to be used for resubmission testing.
        # Need to be in the disseminated state in order to re-disseminated
        disseminated = complete_resubmission(old_sac, new_sac, THE_USER_OBJ)
        APNE(old_sac, new_sac)

        if disseminated:
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
