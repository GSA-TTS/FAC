import logging
from copy import deepcopy

logger = logging.getLogger(__name__)


# This transform is needed for backwards compatibility with workbook templates 1.0.0 and 1.0.1
def rename_additional_notes_sheet_to_form_sheet(ir):
    new_ir = deepcopy(ir)

    for sheet in new_ir:
        if sheet["name"] == "AdditionalNotes":
            sheet["name"] = "Form"

    return new_ir
