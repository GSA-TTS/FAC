from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist
import logging
from curation.curationlib.update_after_submission import (
    check_report_disseminated,
    get_sac_with_ein_to_update,
    get_sac_with_report_id,
    get_sac_with_uei,
    status_to_bool,
    update_ein,
    update_authorized_public,
    update_uei,
)

import sys
from users.models import StaffUser
from audit.validators import validate_uei
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import re

logger = logging.getLogger(__name__)


def nonelike(v):
    return v is None or v == "" or v == {} or v == []


def validate_uei_options(options):
    try:
        # We use a .get(), which will fail if there is more than one.
        _ = get_sac_with_uei(options)
        ok_old_uei = True
    except Exception as e:
        logger.error(e)
        logger.error(f"could not fetch report_id {options['report_id']}")
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
    return ok_old_uei, ok_new_uei


def validate_ein_options(options):
    try:
        _ = get_sac_with_ein_to_update(options)
        ok_old_ein = re.match("[0-9]{9}", options["old_ein"])
        if not ok_old_ein:
            logger.error(f"The EIN {options['old_ein']} is not nine digits.")
    except Exception as e:
        logger.error(e)
        logger.error(f"could not fetch {options['report_id']}")
        ok_old_ein = False

    # All we can assert is an EIN is nine digits.
    try:
        ok_new_ein = re.match("[0-9]{9}", options["new_ein"])
        if not ok_new_ein:
            logger.error(f"The EIN {options['new_ein']} is not nine digits.")
    except ValidationError:
        logger.error("new_ein is not valid")
        ok_new_ein = False
    return ok_old_ein, ok_new_ein


def validate_authorized_options(options):
    old_authorized_opt = status_to_bool(options["old_authorization"])
    new_authorized_opt = status_to_bool(options["new_authorization"])

    # The old value needs to match what is in the DB.
    try:
        sac = get_sac_with_report_id(options)
        entity_type = sac.general_information["user_provided_organization_type"]
        if entity_type != "tribal":
            logger.error("Cannot change the status of a non-tribal organization.")
            return False, False
        elif entity_type == "tribal":
            status_in_db = status_to_bool(
                sac.tribal_data_consent["is_tribal_information_authorized_to_be_public"]
            )
        else:
            logger.error("Should not get here. Entity type check failed. Exiting.")
            sys.exit(-1)
        # If they are the same, we're good.
        # That is, both true or both false.
        # Use XOR. In Python: https://stackoverflow.com/a/433161
        ok_old_authorized = status_in_db == old_authorized_opt
    except ObjectDoesNotExist as e:
        logger.error(e)
        logger.error(f"could not fetch {options['report_id']}")
        ok_old_authorized = False

    # The old status must match in the DB.
    if not ok_old_authorized:
        logger.error(
            f"Old status must match; DB: {status_in_db} you: {old_authorized_opt}"
        )

    # The new value just needs to be opposite the old.
    if old_authorized_opt == new_authorized_opt:
        logger.error(
            f"Status must change. DB: {old_authorized_opt} New: {new_authorized_opt}"
        )
        ok_new_authorized = False
    else:
        ok_new_authorized = True

    return ok_old_authorized, ok_new_authorized


def have_pair_of(flag, options):
    old_flag = f"old_{flag}"
    new_flag = f"new_{flag}"
    return not nonelike(options[old_flag]) and not nonelike(options[new_flag])


def just_one_pair(flags, options):
    pair_count = 0
    for flag in flags:
        pair_count += 1 if have_pair_of(flag, options) else 0
    if pair_count != 1:
        logger.error("You have multiple pairs. Exiting.")
        return False
    return True


def validate_combos(options):
    # We should only get one pair at a time.
    if not just_one_pair(["uei", "ein", "authorization"], options):
        return False

    # We either need a pair of UEIs, or a pair of EINs.
    # Do we have a pair of UEIs?
    if have_pair_of("uei", options):
        ok_old_uei, ok_new_uei = validate_uei_options(options)
        return ok_old_uei and ok_new_uei

    # Do we have a pair of EINs?
    elif have_pair_of("ein", options):
        ok_old_ein, ok_new_ein = validate_ein_options(options)
        return ok_old_ein and ok_new_ein

    # Or a pair of suppression flags?
    elif have_pair_of("authorization", options):
        ok_old_suppression, ok_new_suppression = validate_authorized_options(options)
        return ok_old_suppression and ok_new_suppression

    # Otherwise, let the user know this won't work.
    else:
        logger.error("You must provide an old/new pair")
        return False


def validate_inputs(options):
    # We have to check all of the options passed.
    # Those checks need to be against the database.

    # Does the report id exist? Is it tribal?
    try:
        ok_report_id = SingleAuditChecklist.objects.get(report_id=options["report_id"])
    except SingleAuditChecklist.DoesNotExist:
        logger.error("report_id not found")
        return False

    # Is it disseminated?
    is_disseminated = check_report_disseminated(options)
    if not is_disseminated:
        logger.error(f"The report {options['report_id']} is not disseminated. Exiting.")
        return False

    # And, did they provide a staff user email?
    # (Note that they had to have privs in TF and be able to
    # enable SSH inproduction in order to get here.)
    try:
        ok_staff_user = StaffUser.objects.get(staff_email=options["email"])
    except StaffUser.DoesNotExist:
        logger.error(f'Staff user {options["email"]} does not exist')
        return False

    # combo OK?
    ok_combo = validate_combos(options)

    # We wouldn't be here if these were not all OK, but we'll and
    # them together for confidence.
    return ok_report_id and ok_staff_user and is_disseminated and ok_combo


class Command(BaseCommand):
    """Updates auditee UEI, EIN, or Tribal suppression status after submission."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--report_id",
            type=str,
            required=True,
            help="Report id that we will modify",
        )

        # Apparently I cannot build a mutex of groups?
        # https://github.com/python/cpython/issues/101337
        # So, I'll enforce the mutual exclusion in `validate_inputs`
        # https://stackoverflow.com/a/30378505
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
            "--new_authorization",
            type=str,
            help="Current authorization to be public status (YES/NO)",
        )
        parser.add_argument(
            "--old_authorization",
            type=str,
            help="Old authorization to be public status (YES/NO)",
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

        if not nonelike(options["old_uei"]) and not nonelike(options["new_uei"]):
            update_uei(options)
        elif not nonelike(options["old_ein"]) and not nonelike(options["new_ein"]):
            update_ein(options)
        elif not nonelike(options["old_authorization"]) and not nonelike(
            options["new_authorization"]
        ):
            update_authorized_public(options)
