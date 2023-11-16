from collections import namedtuple as NT

BaseFieldMap = NT("BaseFieldMap", "in_db in_dissem default type")

FormFieldInDissem = WorkbookFieldInDissem = 1000


# This provides a way to map the sheet in the workbook to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before filling in the XLSX workbooks.
class SheetFieldMap(BaseFieldMap):
    _fields = ("in_sheet",) + BaseFieldMap._fields


# This provides a way to map fields in the form to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before creating an initial sac.
class FormFieldMap(BaseFieldMap):
    _fields = ("in_form",) + BaseFieldMap._fields
