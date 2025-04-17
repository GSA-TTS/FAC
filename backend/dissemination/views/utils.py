from datetime import datetime

from users.permissions import can_read_tribal


def include_private_results(request):
    """
    Determine if the user is authenicated to see private data.
    """
    if not request.user.is_authenticated:
        return False

    if not can_read_tribal(request.user):
        return False

    return True


def to_date(date_string):
    """
    Helper method to convert a string in the format YYYY-MM-DD to a date object.
    """
    return datetime.strptime(date_string, "%Y-%m-%d").date()
