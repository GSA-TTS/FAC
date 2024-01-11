import logging

from django.apps import apps
from django.conf import settings

from ..exception_utils import DataMigrationError
from .general_information import (
    general_information,
)
from .audit_information import (
    audit_information,
)
from .auditee_certification import (
    auditee_certification,
)
from .auditor_certification import (
    auditor_certification,
)
from .report_id_generator import (
    xform_dbkey_to_report_id,
)
from ..transforms.xform_string_to_string import (
    string_to_string,
)

logger = logging.getLogger(__name__)


def setup_sac(user, audit_header):
    """Create a SAC object for the historic data migration."""
    if user is None:
        raise DataMigrationError(
            "No user provided to setup sac object",
            "invalid_user",
        )

    logger.info(f"Creating a SAC object for {user}")

    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    generated_report_id = xform_dbkey_to_report_id(audit_header)

    try:
        exists = SingleAuditChecklist.objects.get(report_id=generated_report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    general_info = general_information(audit_header)

    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=general_info,
        audit_information=audit_information(audit_header),
        audit_type=general_info["audit_type"],
    )

    sac.report_id = generated_report_id
    Access = apps.get_model("audit.Access")
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )

    # We need these to be different.
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email="fac-census-migration-auditor-official@fac.gsa.gov",
        role="certifying_auditor_contact",
    )

    sac.auditee_certification = auditee_certification(audit_header)
    sac.auditor_certification = auditor_certification(audit_header)
    sac.data_source = settings.CENSUS_DATA_SOURCE

    if general_info["user_provided_organization_type"] == "tribal":
        suppression_code = string_to_string(audit_header.SUPPRESSION_CODE).upper()
        sac.tribal_data_consent = {
            "tribal_authorization_certifying_official_title": settings.GSA_MIGRATION,
            "is_tribal_information_authorized_to_be_public": suppression_code != "IT",
            "tribal_authorization_certifying_official_name": settings.GSA_MIGRATION,
        }

    sac.save()
    logger.info("Created single audit checklist %s", sac)

    return sac
