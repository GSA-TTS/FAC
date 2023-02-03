from django.contrib.auth import backends, get_user_model
from djangooidc.backends import OpenIdConnectBackend

from audit.models import Access

import logging

UserModel = get_user_model()

logger = logging.getLogger(__name__)


def claim_audit_access(user, all_emails):
    access_invites = (
        Access.objects.filter(user_id=None)
        .filter(email__in=all_emails)
        .update(user_id=user.id)
    )
    logger.debug(f"{user.email} granted access to {access_invites} new audits")


class FACAuthenticationBackend(OpenIdConnectBackend):
    def authenticate(self, request, **user_info):
        user = super().authenticate(request, **user_info)
        if user:
            all_emails = user_info.get("all_emails", [])
            claim_audit_access(user, all_emails)

        return user


class FACTestAuthenticationBackend(backends.BaseBackend):
    """
    Backend for testing purposes which automatically creates (if necessary) and
    returns a user with the provided username
    """

    def authenticate(self, request, **kwargs):
        user, _ = UserModel.objects.get_or_create(username=kwargs["username"])
        return user
