from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist, User, SubmissionEvent
import logging
from curation.curationlib.curation_audit_tracking import CurationTracking
import sys
from users.models import StaffUser
from audit.validators import validate_uei
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction
from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    Passthrough,
    SecondaryAuditor,
)

logger = logging.getLogger(__name__)


def get_named_models():
    return {
        "AdditionalEins": AdditionalEin,
        "AdditionalUeis": AdditionalUei,
        "CorrectiveActionPlan": CapText,
        "FederalAwards": FederalAward,
        "FindingsText": FindingText,
        "FindingsUniformGuidance": Finding,
        "NotesToSefa": Note,
        "SecondaryAuditors": SecondaryAuditor,
        "General": General,
        "Passthrough": Passthrough,
    }


def get_named_parts(sac):
    return {
        "AdditionalEins": sac.additional_eins,
        "AdditionalUeis": sac.additional_ueis,
        "CorrectiveActionPlan": sac.corrective_action_plan,
        "FederalAwards": sac.federal_awards,
        "FindingsText": sac.findings_text,
        "FindingsUniformGuidance": sac.findings_uniform_guidance,
        "NotesToSefa": sac.notes_to_sefa,
        "SecondaryAuditors": sac.secondary_auditors,
    }


def validate_inputs(options):
    # We have to check all of the options passed.

    # Does the report id exist?
    try:
        ok_report_id = SingleAuditChecklist.objects.get(report_id=options["report_id"])
    except SingleAuditChecklist.DoesNotExist:
        logger.error("report_id not found")
        ok_report_id = False

    # We either need a pair of UEIs, or a pair of EINs.
    if "old_uei" in options and "new_uei" in options:
        # Does the old UEI exist?
        crit1 = Q(report_id=options["report_id"])
        crit2 = Q(general_information__auditee_uei=options["old_uei"])
        count = SingleAuditChecklist.objects.filter(crit1 & crit2).count()
        if count == 1:
            ok_old_uei = True
        else:
            logger.error("old_uei not found for report_id")
            ok_old_uei = False

        # New UEI?
        # Hm. The new UEI might not be in the database.
        # We could validate against SAM here. For now, we'll make sure
        # it is a valid-shaped UEI.
        try:
            ok_new_uei = validate_uei(options["new_uei"])
        except ValidationError:
            logger.error("new_uei is not valid")
            ok_new_uei = False

    elif "old_ein" in options and "new_ein" in options:
        # Does the old UEI exist?
        crit1 = Q(report_id=options["report_id"])
        crit2 = Q(general_information__ein=options["old_ein"])
        count = SingleAuditChecklist.objects.filter(crit1 & crit2).count()
        if count == 1:
            ok_new_ein = True
        else:
            logger.error("old_ein not found for report_id")
            ok_new_ein = False

        # New UEI?
        # Hm. The new UEI might not be in the database.
        # We could validate against SAM here. For now, we'll make sure
        # it is a valid-shaped UEI.
        try:
            ok_new_uei = validate_uei(options["new_uei"])
        except ValidationError:
            logger.error("new_uei is not valid")
            ok_new_uei = False
    else:
        logger.error("You must provide either an old/new UEI or old/new EIN")
        return False

    # And, did they provide a staff user email?
    # (Note that they had to have privs in TF and be able to
    # enable SSH inproduction in order to get here.)
    try:
        ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
    except StaffUser.DoesNotExist:
        logger.error("staff user does not exist")
        ok_staff_user = False

    return ok_report_id and ok_old_uei and (ok_new_uei or ok_new_ein) and ok_staff_user


def update_uei(options):
    # If we get here, the parameters validated.
    # Now we need to pull the SAC, update the record, and
    # save the new UEI.
    THE_NEW_UEI = options["new_uei"]

    # Note that the UEI is not only in the general info, but
    # also in every one of the workbooks. Too bad we stored it that way.
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__auditee_uei=options["old_uei"])
    # We already validated that there will only be one object coming back.
    sac = SingleAuditChecklist.objects.get(crit1 & crit2)
    named_parts = get_named_parts(sac)

    logger.info("Updating SAC: " + str(sac))
    THE_USER_OBJ = User.objects.get(email=options["email"])

    sac.general_information["auditee_uei"] = THE_NEW_UEI
    for json_field, object in named_parts.items():
        # We might not have this workbook.
        if object:
            # If we do have the workbook, we MUST have auditee_uei as a field.
            if json_field in object:
                object[json_field]["auditee_uei"] = THE_NEW_UEI
            else:
                logger.error("Could not find auditee_uei in XLSX JSON object")
                sys.exit(-1)

    with transaction.atomic():
        sac.save(
            administrative_override=True,
            event_user=THE_USER_OBJ,
            event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_UEI_REPLACEMENT,
        )
        sac.redisseminate()


def update_ein(options):
    # Now we need to pull the SAC, update the record, and
    # save the new EIN.
    THE_NEW_EIN = options["new_ein"]

    # The EIN is only in the general info.
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__auditee_uei=options["old_ein"])
    # We already validated that there will only be one object coming back.
    sac = SingleAuditChecklist.objects.get(crit1 & crit2)

    logger.info("Updating SAC: " + str(sac))
    THE_USER_OBJ = User.objects.get(email=options["email"])

    sac.general_information["auditee_ein"] = THE_NEW_EIN

    with transaction.atomic():
        sac.save(
            administrative_override=True,
            event_user=THE_USER_OBJ,
            event_type=SubmissionEvent.EventType.FAC_ADMINISTRATIVE_EIN_REPLACEMENT,
        )
        sac.redisseminate()


class Command(BaseCommand):
    """Updates the UEI for a previously submitted audit."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--report_id",
            type=str,
            required=True,
            help="Report id that we will modify",
        )

        parser.add_argument(
            "--old_uei",
            type=str,
            help="The UEI that is currently in place",
        )
        parser.add_argument(
            "--new_uei",
            type=str,
            help="The new UEI for this report",
        )

        # FIX: group one or the other
        parser.add_argument(
            "--old_ein",
            type=str,
            help="The EIN that is currently in place",
        )
        parser.add_argument(
            "--new_ein",
            type=str,
            help="The new EIN for this report",
        )

        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="The email of the FAC staff making this change",
        )

    def handle(self, *args, **options):

        valid_inputs = validate_inputs(options)
        if not valid_inputs:
            logger.error("inputs were not valid")
            sys.exit(-1)

        if "old_uei" in options and "new_uei" in options:
            update_uei(options)
        elif "old_ein" in options and "new_ein" in options:
            update_ein(options)
