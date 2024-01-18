import copy
from typing import Any


class InspectionRecord:
    """Hold a record of changes for the ongoing report migration"""

    # It was decided that changes should be recorded as lists of equal size
    # within the following fields: `finding`, `federal_award`, `secondary_auditor`, `cap_text`, `passthrough`, and `finding_text`.
    # That is, `finding`: [change_list_1, change_list_2, ...] where all change_list_i have the same size.
    # This is to ensure that change records maintains the same order as the original records.
    # This does not apply to `general` and `note`, as we have a one-to-one relationship between an audit report and each of these fields.

    DEFAULT: dict[str, Any] = {
        "general": [],
        "finding": [],
        "finding_text": [],
        "additional_ein": [],
        "additional_uei": [],
        "note": [],
        "passthrough": [],
        "cap_text": [],
        "secondary_auditor": [],
        "federal_award": [],
    }
    change = copy.deepcopy(DEFAULT)

    @staticmethod
    def reset():
        InspectionRecord.change = copy.deepcopy(InspectionRecord.DEFAULT)

    @staticmethod
    def append_finding_changes(data):
        InspectionRecord.change["finding"].append(data)

    @staticmethod
    def append_note_changes(data):
        InspectionRecord.change["note"].append(data)

    @staticmethod
    def append_general_changes(data):
        InspectionRecord.change["general"].append(data)

    @staticmethod
    def append_federal_awards_changes(data):
        InspectionRecord.change["federal_award"].append(data)


class CensusRecord:
    def __init__(self, column="", value=""):
        self.column = column
        self.value = value

    def to_dict(self):
        return {"column": self.column, "value": self.value}


class GsaFacRecord:
    def __init__(self, field="", value=""):
        self.field = field
        self.value = value

    def to_dict(self):
        return {"field": self.field, "value": self.value}
