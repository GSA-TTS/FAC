import logging
import sys

from users.models import StaffUser

logger = logging.getLogger(__name__)


def exit_if_not_staff_user(email):
    """
    Exits if the given email doesn't belong to a staff member
    """
    try:
        ok_staff_user = StaffUser.objects.get(staff_email=email)
    except StaffUser.DoesNotExist:
        logger.error(f"Staff user {email} does not exist")
        ok_staff_user = False

    if not ok_staff_user:
        sys.exit(-1)


def order_reports_key(r):
    for ndx, tn in enumerate(list(reversed(r.transition_name))):
        if tn == "submitted":
            break
    return list(reversed(r.transition_date))[ndx]
