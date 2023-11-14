from collections import namedtuple as NT

BaseFieldMap = NT("BaseFieldMap", "in_db in_dissem default type")

FormFieldInDissem = WorbookFieldInDissem = 1000


class SheetFieldMap(BaseFieldMap):
    _fields = ("in_sheet",) + BaseFieldMap._fields


class FormFieldMap(BaseFieldMap):
    _fields = ("in_form",) + BaseFieldMap._fields
