import logging

from django.apps import apps
from django.conf import settings

from .cognizant_oversight import cognizant_oversight

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


# !!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!
# This was quickly updated to handle SOT, with minimal testing outside unit tests.
# The idea was this code is legacy, and shouldn't actually be needed, but does have
# some valuable tools for workbook translations. Rather than try and pull out the workbook
# translations separately, in order to launch SOT quicly, I updated this code to pass
# unit tests. Use of this code for its original purpose of migrating census data
# into SAC data is not advised unless it is thoroughly tested.
def setup_audit(user, audit_header):
    """Create an Audit object for the historic data migration."""
    if user is None:
        raise DataMigrationError(
            "No user provided to setup sac object",
            "invalid_user",
        )

    logger.info(f"Creating a SAC object for {user}")

    Audit = apps.get_model("audit.Audit")
    generated_report_id = xform_dbkey_to_report_id(audit_header)

    try:
        exists = Audit.objects.get(report_id=generated_report_id)
    except Audit.DoesNotExist:
        exists = None
    if exists:
        exists.delete()

    general_info = general_information(audit_header)

    cognizant, oversight = cognizant_oversight(audit_header)
    audit_data = {
        "general_information": general_info,
        "audit_information": audit_information(audit_header),
        "auditee_certification": auditee_certification(audit_header),
        "auditor_certification": auditor_certification(audit_header),
        "cognizant_agency": cognizant,
        "oversight_agency": oversight,
    }
    if general_info["user_provided_organization_type"] == "tribal":
        suppression_code = string_to_string(audit_header.SUPPRESSION_CODE).upper()
        audit_data |= {
            "tribal_data_consent": {
                "tribal_authorization_certifying_official_title": settings.GSA_MIGRATION,
                "is_tribal_information_authorized_to_be_public": suppression_code
                != "IT",
                "tribal_authorization_certifying_official_name": settings.GSA_MIGRATION,
            }
        }
    audit = Audit.objects.create(
        event_user=user,
        event_type="CENSUS-MIGRATION",
        audit=audit_data,
        data_source=settings.CENSUS_DATA_SOURCE,
        audit_type=general_info["audit_type"],
    )

    audit.report_id = generated_report_id
    Access = apps.get_model("audit.Access")
    Access.objects.create(
        audit=audit,
        user=user,
        email=user.email,
        role="editor",
    )

    # We need these to be different.
    Access.objects.create(
        audit=audit,
        user=user,
        email=user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        audit=audit,
        user=user,
        email="fac-census-migration-auditor-official@fac.gsa.gov",
        role="certifying_auditor_contact",
    )

    logger.info("Created audit %s", audit)

    return audit
