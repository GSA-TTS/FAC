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
        "validations_to_skip": [],
        "invalid_migration_tag": [],
    }
    fields = copy.deepcopy(DEFAULT)

    @staticmethod
    def reset():
        InvalidRecord.fields = copy.deepcopy(InvalidRecord.DEFAULT)

    @staticmethod
    def append_invalid_finding_records(data):
        InvalidRecord.fields["finding"].append(data)

    @staticmethod
    def append_invalid_note_records(data):
        InvalidRecord.fields["note"].append(data)

    @staticmethod
    def append_invalid_general_records(data):
        InvalidRecord.fields["general"].append(data)

    @staticmethod
    def append_invalid_federal_awards_records(data):
        InvalidRecord.fields["federal_award"].append(data)

    @staticmethod
    def append_invalid_secondary_auditor_records(data):
        InvalidRecord.fields["secondary_auditor"].append(data)

    @staticmethod
    def append_invalid_additional_ein_records(data):
        InvalidRecord.fields["additional_ein"].append(data)

    @staticmethod
    def append_invalid_additional_uei_records(data):
        InvalidRecord.fields["additional_uei"].append(data)

    @staticmethod
    def append_invalid_passthrough_records(data):
        InvalidRecord.fields["passthrough"].append(data)

    @staticmethod
    def append_invalid_cap_text_records(data):
        InvalidRecord.fields["cap_text"].append(data)

    @staticmethod
    def append_invalid_finding_text_records(data):
        InvalidRecord.fields["finding_text"].append(data)

    @staticmethod
    def append_validations_to_skip(data):
        InvalidRecord.fields["validations_to_skip"].append(data)

    @staticmethod
    def append_invalid_migration_tag(data):
        InvalidRecord.fields["invalid_migration_tag"].append(data)
