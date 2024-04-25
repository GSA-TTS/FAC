"""
Keeping this in a separate file allows us to re-use the same list in both Access and
DeletedAccess without running into circular import problems.
"""

from django.utils.translation import gettext_lazy as _

ACCESS_ROLES = (
    ("certifying_auditee_contact", _("Auditee Certifying Official")),
    ("certifying_auditor_contact", _("Auditor Certifying Official")),
    ("editor", _("Audit Editor")),
)
