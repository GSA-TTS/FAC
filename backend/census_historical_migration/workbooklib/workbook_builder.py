from django.core.files.uploadedfile import SimpleUploadedFile
from fs.memoryfs import MemoryFS

from ..workbooklib.excel_creation_utils import (
    get_template_name_for_section,
)

import logging

logger = logging.getLogger(__name__)


def _make_excel_file(filename, f_obj):
    content = f_obj.read()
    f_obj.seek(0)
    file = SimpleUploadedFile(filename, content, "application/vnd.ms-excel")
    return file


def generate_workbook(workbook_generator, audit_header, section):
    """
    Generates a workbook in memory using the workbook_generator for a given audit_header
    and section template name. Returns the workbook object, its JSON data representation,
    the Excel file as a SimpleUploadedFile object, and the filename.
    """
    with MemoryFS() as mem_fs:
        # Define the filename based on the section template name and dbkey
        filename = (
            get_template_name_for_section(section)
            .replace(".xlsx", "-{}.xlsx")
            .format(audit_header.DBKEY)
        )
        with mem_fs.openbin(filename, mode="w") as outfile:
            # Generate the workbook object along with the API JSON representation
            wb = workbook_generator(audit_header, outfile)

        # Re-open the file in read mode to create an Excel file object
        with mem_fs.openbin(filename, mode="r") as outfile:
            excel_file = _make_excel_file(filename, outfile)

        return wb, excel_file, filename
