import copy
from typing import Any


class InvalidRecord:
    """Hold invalid record for the ongoing report migration"""

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
        InvalidRecord.change = copy.deepcopy(InvalidRecord.DEFAULT)

    @staticmethod
    def append_finding_changes(data):
        InvalidRecord.change["finding"].append(data)

    @staticmethod
    def append_note_changes(data):
        InvalidRecord.change["note"].append(data)

    @staticmethod
    def append_general_changes(data):
        InvalidRecord.change["general"].append(data)

    @staticmethod
    def append_federal_awards_changes(data):
        InvalidRecord.change["federal_award"].append(data)

    @staticmethod
    def append_secondary_auditor_changes(data):
        InvalidRecord.change["secondary_auditor"].append(data)
