from fs.memoryfs import MemoryFS

from census_historical_migration.workbooklib.sac_creation import (
    _post_upload_workbook,
    _make_excel_file,
    _create_test_sac,
)
from audit.fixtures.excel import FORM_SECTIONS
from django.apps import apps


from census_historical_migration.workbooklib.notes_to_sefa import generate_notes_to_sefa
from census_historical_migration.workbooklib.federal_awards import (
    generate_federal_awards,
)
from census_historical_migration.workbooklib.findings import generate_findings
from census_historical_migration.workbooklib.findings_text import generate_findings_text
from census_historical_migration.workbooklib.corrective_action_plan import (
    generate_corrective_action_plan,
)
from census_historical_migration.workbooklib.additional_ueis import (
    generate_additional_ueis,
)
from census_historical_migration.workbooklib.additional_eins import (
    generate_additional_eins,
)
from census_historical_migration.workbooklib.secondary_auditors import (
    generate_secondary_auditors,
)

import logging

sections = {
    FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: generate_federal_awards,
    FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}

filenames = {
    FORM_SECTIONS.ADDITIONAL_EINS: "additional-eins-{}.xlsx",
    FORM_SECTIONS.ADDITIONAL_UEIS: "additional-ueis-{}.xlsx",
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: "corrective-action-plan-{}.xlsx",
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-{}.xlsx",
    FORM_SECTIONS.FINDINGS_TEXT: "audit-findings-text-{}.xlsx",
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: "audit-findings-{}.xlsx",
    FORM_SECTIONS.NOTES_TO_SEFA: "notes-to-sefa-{}.xlsx",
    FORM_SECTIONS.SECONDARY_AUDITORS: "secondary-auditors-{}.xlsx",
}

logger = logging.getLogger(__name__)


def setup_sac(user, test_name, dbkey):
    if user is None:
        logger.error("No user provided to setup_sac")
        return
    logger.info(f"Creating a SAC object for {user}, {test_name}")
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")

    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=test_name
    ).first()

    logger.info(sac)
    if sac is None:
        sac = _create_test_sac(user, test_name, dbkey)
    return sac


def generate_workbook(workbook_generator, dbkey, year, section):
    with MemoryFS() as mem_fs:
        filename = filenames[section].format(dbkey)
        with mem_fs.openbin(filename, mode="w") as outfile:
            # Generate the workbook object along with the API JSON representation
            wb, json_data = workbook_generator(dbkey, year, outfile)

        # Re-open the file in read mode to create an Excel file object
        with mem_fs.openbin(filename, mode="r") as outfile:
            excel_file = _make_excel_file(filename, outfile)

        return wb, json_data, excel_file, filename


def workbook_loader(user, sac, dbkey, year):
    def _loader(workbook_generator, section):
        wb, json_data, excel_file, filename = generate_workbook(
            workbook_generator, dbkey, year, section
        )

        if user:
            _post_upload_workbook(sac, user, section, excel_file)

        return wb, json_data, filename

    return _loader
