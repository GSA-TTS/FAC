from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist
import logging
from curation.curationlib.curation_audit_tracking import CurationTracking
import sys
from users.models import StaffUser
from audit.validators import validate_uei
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction


logger = logging.getLogger(__name__)


def validate_inputs(options):
    # We have to check all of the options passed.

    # Does the report id exist?
    try:
        ok_report_id = SingleAuditChecklist.objects.get(report_id=options["report_id"])
    except SingleAuditChecklist.DoesNotExist:
        print("report_id not found")
        ok_report_id = False

    # Does the old UEI exist?
    crit1 = Q(report_id=options["report_id"])
    crit2 = Q(general_information__auditee_uei=options["old_uei"])
    count = SingleAuditChecklist.objects.filter(crit1 & crit2).count()
    if count == 1:
        ok_old_uei = True
    else:
        ok_old_uei = False

    # New UEI?
    # Hm. The new UEI might not be in the database.
    # We could validate against SAM here. For now, we'll make sure
    # it is a valid-shaped UEI.
    try:
        ok_new_uei = validate_uei(options["new_uei"])
    except ValidationError:
        print("new_uei is not valid")
        ok_new_uei = False

    # And, did they provide a staff user email?
    # (Note that they had to have privs in TF and be able to
    # enable SSH inproduction in order to get here.)
    try:
        ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
    except StaffUser.DoesNotExist:
        print("staff user does not exist")
        ok_staff_user = False

    return ok_report_id and ok_old_uei and ok_new_uei and ok_staff_user


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
            required=True,
            help="The UEI that is currently in place",
        )
        parser.add_argument(
            "--new_uei",
            type=str,
            required=True,
            help="The new UEI for this report",
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
            print("inputs were not valid")
            sys.exit(-1)

        # If we get here, the parameters validated.
        # Now we need to pull the SAC, update the record, and
        # save the new UEI.
        THE_NEW_UEI = options["new_uei"]

        #
        # Note that the UEI is not only in the general info, but
        # also in every one of the workbooks. Too bad we stored it that way.
        crit1 = Q(report_id=options["report_id"])
        crit2 = Q(general_information__auditee_uei=options["old_uei"])
        # There should only be one matching object here.
        # If there isn't, our validation is bad, and we should throw an
        # exception at this point.
        try:
            sac = SingleAuditChecklist.objects.get(crit1 & crit2)
        except SingleAuditChecklist.MultipleObjectsReturned:
            print("we found multiple SACs with report_id/uei. exiting.")
            sys.exit(-1)

        parts = {
            "NotesToSefa": sac.notes_to_sefa,
            "FederalAwards": sac.federal_awards,
            "CorrectiveActionPlan": sac.corrective_action_plan,
            "FindingsText": sac.findings_text,
            "FindingsUniformGuidance": sac.findings_uniform_guidance,
            "AdditionalUeis": sac.additional_ueis,
            "AdditionalEins": sac.additional_eins,
            "SecondaryAuditors": sac.secondary_auditors,
        }
        with transaction.atomic():
            sac.general_information["auditee_uei"] = THE_NEW_UEI
            for json_field, object in parts.items():
                if object:
                    object[json_field]["auditee_uei"] = THE_NEW_UEI
            sac.save()
