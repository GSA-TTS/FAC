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
