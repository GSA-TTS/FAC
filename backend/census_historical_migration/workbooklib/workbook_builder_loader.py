from census_historical_migration.workbooklib.workbook_builder import generate_workbook
from census_historical_migration.workbooklib.post_upload_utils import (
    _post_upload_workbook,
)

import logging

logger = logging.getLogger(__name__)


def workbook_builder_loader(user, sac, dbkey, year):
    """
    Returns a nested function '_loader' that, when called with a workbook generator
    and a section, generates a workbook for the section, uploads it to SAC,
    and returns the workbook, its associated JSON data, and filename.
    """

    def _loader(workbook_generator, section):
        wb, json_data, excel_file, filename = generate_workbook(
            workbook_generator, dbkey, year, section
        )

        if user:
            _post_upload_workbook(sac, user, section, excel_file)
        else:
            raise Exception("User must be provided to upload workbook")

        return wb, json_data, filename

    return _loader
