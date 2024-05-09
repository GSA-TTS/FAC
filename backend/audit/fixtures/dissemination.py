"""
Fixtures for dissemination models.
We want a few example submissions for testing front end accessibility.
"""

import logging
from model_bakery import baker
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    FindingText,
    Note,
    CapText,
)

logger = logging.getLogger(__name__)

sac_info_without_findings = {
    "auditee_name": "Test SAC - No findings",
    "auditee_uei": "GSA_TESTDATA",
    "audit_year": "2024",
    "report_id": "2024-06-TSTDAT-0000000001",
}


def load_dissemination():
    """
    Generate an example SAC with an accompanying award.
    """
    logger.info("Creating example SACs for dissemination.")

    report_id_no_findings = sac_info_without_findings.get("report_id", "")
    sac_no_findings = General.objects.filter(
        report_id=report_id_no_findings,
    ).first()
    if sac_no_findings is None:
        general_no_findings = baker.make(General, **sac_info_without_findings)
        baker.make(FederalAward, report_id=general_no_findings)
        logger.info("Created SAC example %s", report_id_no_findings)
    else:
        logger.info("SAC %s already exists, skipping.", report_id_no_findings)
