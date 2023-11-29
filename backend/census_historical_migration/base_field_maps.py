FormFieldInDissem = WorkbookFieldInDissem = 1000


class BaseFieldMap:
    def __init__(self, in_db, in_dissem, default, type):
        self.in_db = in_db
        self.in_dissem = in_dissem
        self.default = default
        self.type = type


# This provides a way to map the sheet in the workbook to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before filling in the XLSX workbooks.
# Define a new named tuple with an additional field
class SheetFieldMap(BaseFieldMap):
    def __init__(self, in_sheet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_sheet = in_sheet


# This provides a way to map fields in the form to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before creating an initial sac.
class FormFieldMap(BaseFieldMap):
    def __init__(self, in_form, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_form = in_form
