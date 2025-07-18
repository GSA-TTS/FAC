from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist
import logging
from curation.curationlib.update_uei_or_ein import (
    update_uei,
    update_ein,
    get_uei_to_update,
    get_ein_to_update,
    check_report_disseminated,
)

import sys
from users.models import StaffUser
from audit.validators import validate_uei
from django.core.exceptions import ValidationError
import re

logger = logging.getLogger(__name__)


def validate_uei_options(options):
    try:
        # We use a .get(), which will fail if there is more than one.
        _ = get_uei_to_update(options)
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
        _ = get_ein_to_update(options)
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


def validate_inputs(options):
    # We have to check all of the options passed.
    # Those checks need to be against the database.

    # Does the report id exist?
    try:
        ok_report_id = SingleAuditChecklist.objects.get(report_id=options["report_id"])
    except SingleAuditChecklist.DoesNotExist:
        logger.error("report_id not found")
        ok_report_id = False

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
        logger.error(f"Staff user {options["email"]} does not exist")  
        ok_staff_user = False

    # We either need a pair of UEIs, or a pair of EINs.
    # Do we have a pair of UEIs?
    if options["old_uei"] is not None and options["new_uei"] is not None:
        ok_old_uei, ok_new_uei = validate_uei_options(options)
        return ok_report_id and (ok_old_uei and ok_new_uei) and ok_staff_user

    # Do we have a pair of EINs?
    elif options["old_ein"] is not None and options["new_ein"] is not None:
        ok_old_ein, ok_new_ein = validate_ein_options(options)
        return ok_report_id and (ok_old_ein and ok_new_ein) and ok_staff_user
    # Did we mix-and-match between EIN and UEI?
    elif options["old_ein"] is not None and options["new_uei"] is not None:
        logger.error("You provided an old EIN and new UEI. Exiting.")
        return False
    # or the other way around?
    elif options["old_uei"] is not None and options["new_ein"] is not None:
        logger.error("You provided an old UEI and new EIN. Exiting.")
        return False
    # Otherwise, let the user know this won't work.
    else:
        logger.error("You must provide either an old/new UEI or old/new EIN")
        return False


class Command(BaseCommand):
    """Updates the UEI for a previously submitted audit."""

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

        if options["old_uei"] is not None and options["new_uei"] is not None:
            update_uei(options)
        elif options["old_ein"] is not None and options["new_ein"] is not None:
            update_ein(options)
