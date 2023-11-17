from collections import namedtuple as NT

FormFieldInDissem = WorkbookFieldInDissem = 1000

BaseFieldMap = NT("BaseFieldMap", "in_db in_dissem default type")

# This provides a way to map the sheet in the workbook to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before filling in the XLSX workbooks.
# Define a new named tuple with an additional field
SheetFieldMap = NT("SheetFieldMap", "in_sheet " + " ".join(BaseFieldMap._fields))


# This provides a way to map fields in the form to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before creating an initial sac.
FormFieldMap = NT("FormFieldMap", "in_form " + " ".join(BaseFieldMap._fields))
