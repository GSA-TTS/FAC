import logging

from django.apps import apps
from django.conf import settings

from ..exception_utils import DataMigrationError
from ..workbooklib.excel_creation_utils import get_audit_header
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

logger = logging.getLogger(__name__)


def _create_sac(user, dbkey):
    """Create a SAC object for the historic data migration."""
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    audit_header = get_audit_header(dbkey)
    generated_report_id = xform_dbkey_to_report_id(audit_header, dbkey)

    try:
        exists = SingleAuditChecklist.objects.get(report_id=generated_report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=general_information(audit_header),
        audit_information=audit_information(audit_header),
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


def setup_sac(user, auditee_name, dbkey):
    """Create a SAC object for the historic data migration."""
    if user is None:
        raise DataMigrationError("No user provided to setup sac object")
    logger.info(f"Creating a SAC object for {user}, {auditee_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")

    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=auditee_name
    ).first()

    logger.info(sac)
    if sac is None:
        sac = _create_sac(user, dbkey)
    return sac
