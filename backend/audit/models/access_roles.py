"""
Keeping this in a separate file allows us to re-use the same list in both Access and
DeletedAccess without running into circular import problems.
"""

from django.utils.translation import gettext_lazy as _


class AccessRole:
    CERTIFYING_AUDITEE_CONTACT = "certifying_auditee_contact"
    CERTIFYING_AUDITOR_CONTACT = "certifying_auditor_contact"
    EDITOR = "editor"


ACCESS_ROLES = (
    (AccessRole.CERTIFYING_AUDITEE_CONTACT, _("Auditee Certifying Official")),
    (AccessRole.CERTIFYING_AUDITOR_CONTACT, _("Auditor Certifying Official")),
    (AccessRole.EDITOR, _("Audit Editor")),
)
