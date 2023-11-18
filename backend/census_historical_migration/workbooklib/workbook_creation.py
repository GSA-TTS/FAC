from fs.memoryfs import MemoryFS

from census_historical_migration.workbooklib.sac_creation import (
    make_valid_ir_and_update_sac,
    _make_excel_file,
    _create_test_sac,
)


from .utils import get_template_name_for_section
from audit.models import SingleAuditChecklist
import logging

logger = logging.getLogger(__name__)


def setup_sac(user, test_name, dbkey):
    if user is None:
        logger.error("No user provided to setup_sac")
        return
    logger.info(f"Creating a SAC object for {user}, {test_name}")

    sac = SingleAuditChecklist.objects.filter(
        submitted_by=user, general_information__auditee_name=test_name
    ).first()

    logger.info(sac)
    if sac is None:
        sac = _create_test_sac(user, test_name, dbkey)
    return sac


def generate_workbook(workbook_generator, sac, gen, section):
    with MemoryFS() as mem_fs:
        filename = (
            get_template_name_for_section(section)
            .replace(".xlsx", "-{}.xlsx")
            .format(gen.DBKEY)
        )
        with mem_fs.openbin(filename, mode="w") as outfile:
            # Generate the workbook object along with the API JSON representation
            wb, json_data = workbook_generator(sac, gen, outfile)

        # Re-open the file in read mode to create an Excel file object
        with mem_fs.openbin(filename, mode="r") as outfile:
            excel_file = _make_excel_file(filename, outfile)

        return wb, json_data, excel_file, filename


def workbook_loader(user, sac, gen):
    def _loader(workbook_generator, section):
        wb, json_data, excel_file, filename = generate_workbook(
            workbook_generator, sac, gen, section
        )

        if user:
            make_valid_ir_and_update_sac(sac, user, section, excel_file)

        return wb, json_data, filename

    return _loader
