from djangooidc.backends import OpenIdConnectBackend

from audit.models import Access

import logging

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
