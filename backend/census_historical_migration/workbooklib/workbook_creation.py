from fs.memoryfs import MemoryFS

from census_historical_migration.workbooklib.sac_creation import (
    _post_upload_workbook,
    _make_excel_file,
    _create_test_sac,
)

from django.apps import apps

from .utils import get_template_name_for_section

import logging

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
        filename = (
            get_template_name_for_section(section)
            .replace(".xlsx", "-{}.xlsx")
            .format(dbkey)
        )
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
