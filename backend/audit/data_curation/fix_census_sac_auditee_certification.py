import logging


from django.conf import settings

from census_historical_migration.transforms.xform_string_to_string import (
    string_to_string,
)


logger = logging.getLogger(__name__)


def update_census_sac_auditee_name(sac, audit_header):
    """Fix the erroneous auditee_name and auditee_title in the auditee_certification of a SAC object."""
    auditee_certification = sac.auditee_certification
    auditee_signature = auditee_certification.get("auditee_signature", {})

    # Get auditee name and title from audit_header or default to settings.GSA_MIGRATION
    auditee_name = string_to_string(
        getattr(audit_header, "AUDITEECERTIFYNAME", settings.GSA_MIGRATION)
    )
    auditee_title = string_to_string(
        getattr(audit_header, "AUDITEECERTIFYTITLE", settings.GSA_MIGRATION)
    )
    # Update auditee_signature with new auditee_name and auditee_title
    auditee_signature["auditee_name"] = auditee_name
    auditee_signature["auditee_title"] = auditee_title
    # Update auditee_signature in auditee_certification
    auditee_certification["auditee_signature"] = auditee_signature

    sac.auditee_certification = auditee_certification
    sac.save()
