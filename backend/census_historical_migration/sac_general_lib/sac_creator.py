import logging

from django.apps import apps
from django.conf import settings
from census_historical_migration.sac_general_lib.general_information import (
    _general_information,
)
from census_historical_migration.sac_general_lib.audit_information import (
    _audit_information,
)
from census_historical_migration.sac_general_lib.auditee_certification import (
    _auditee_certification,
)
from census_historical_migration.sac_general_lib.auditor_certification import (
    _auditor_certification,
)
from census_historical_migration.sac_general_lib.report_id_generator import (
    dbkey_to_report_id,
)

from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)

logger = logging.getLogger(__name__)


def _create_sac(user, dbkey):
    """Create a SAC object for the historic data migration."""
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    generated_report_id = dbkey_to_report_id(Gen, dbkey)
    try:
        exists = SingleAuditChecklist.objects.get(report_id=generated_report_id)
    except SingleAuditChecklist.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_general_information(dbkey),
        audit_information=_audit_information(dbkey),
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
        email="fac-census-migration-auditee-official@auditee.org",  # user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email="fac-census-migration-auditor-official@auditor.org",  # user.email,
        role="certifying_auditor_contact",
    )

    sac.auditee_certification = _auditee_certification(dbkey)
    sac.auditor_certification = _auditor_certification(dbkey)
    sac.data_source = settings.CENSUS_DATA_SOURCE
    sac.save()

    logger.info("Created single audit checklist %s", sac)
    return sac


def setup_sac(user, auditee_name, dbkey):
    """Create a SAC object for the historic data migration."""
    if user is None:
        logger.error("No user provided to setup_sac")
        return
    logger.info(f"Creating a SAC object for {user}, {auditee_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")

    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=auditee_name
    ).first()

    logger.info(sac)
    if sac is None:
        sac = _create_sac(user, dbkey)
    return sac
