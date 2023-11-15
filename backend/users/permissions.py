from users.models import Permission, UserPermission


def can_read_tribal(user):
    return (
        UserPermission.objects.filter(
            user=user, permission__slug=Permission.PermissionType.READ_TRIBAL
        ).count()
        > 0
    )
