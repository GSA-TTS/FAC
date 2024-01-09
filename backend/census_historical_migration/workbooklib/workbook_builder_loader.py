from ..workbooklib.workbook_builder import generate_workbook
from ..workbooklib.post_upload_utils import (
    post_upload_workbook,
)

import logging

logger = logging.getLogger(__name__)


def workbook_builder_loader(user, sac, audit_header):
    """
    Returns a nested function '_loader' that, when called with a workbook generator
    and a section, generates a workbook for the section, uploads it to SAC,
    and returns the workbook, its associated JSON data, and filename.
    """

    def _loader(workbook_generator, section):
        wb, excel_file, filename = generate_workbook(
            workbook_generator, audit_header, section
        )

        if user:
            post_upload_workbook(sac, section, excel_file)
        else:
            raise Exception("User must be provided to upload workbook")

        return wb, filename

    return _loader
