import logging

from django.apps import apps
from django.conf import settings

from ..exception_utils import DataMigrationError
from ..sac_general_lib.general_information import (
    general_information,
)
from ..sac_general_lib.audit_information import (
    audit_information,
)
from ..sac_general_lib.auditee_certification import (
    auditee_certification,
)
from ..sac_general_lib.auditor_certification import (
    auditor_certification,
)
from ..sac_general_lib.report_id_generator import (
    xform_dbkey_to_report_id,
)
from ..migration_result import MigrationResult


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
    MigrationResult.result["transformations"].append(
        {
            "section": "General",
            "census_data": audit_header.DBKEY,
            "gsa_fac_data": generated_report_id,
            "transformation_function": "xform_dbkey_to_report_id",
        }
    )

    try:
        exists = SingleAuditChecklist.objects.get(report_id=generated_report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    general_info = general_information(audit_header)
    audit_info = audit_information(audit_header)
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=general_info,
        audit_information=audit_info,
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
    sac.save()
    logger.info("Created single audit checklist %s", sac)
    return sac
