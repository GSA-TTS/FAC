import copy
from typing import Any

from .base_field_maps import WorkbookFieldInDissem

from .workbooklib.excel_creation_utils import apply_conversion_function


class ChangeRecord:
    """Hold a record of changes for the ongoing report migration"""

    # We record changes with respect to dissemination tables.
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
        ChangeRecord.change = copy.deepcopy(ChangeRecord.DEFAULT)

    @staticmethod
    def extend_finding_changes(data):
        ChangeRecord.change["finding"].extend(data)

    @staticmethod
    def extend_note_changes(data):
        ChangeRecord.change["note"].extend(data)

    @staticmethod
    def extend_general_changes(data):
        ChangeRecord.change["general"].extend(data)

    @staticmethod
    def extend_federal_awards_changes(data):
        ChangeRecord.change["federal_award"].extend(data)


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


def retrieve_change_records(mappings, objects):
    """Retrieve change records for the current section"""
    change_records = []  # FIXME: in case we need the table name change to dict
    if mappings and objects:
        for o in objects:
            for m in mappings:
                raw_value = getattr(o, m.in_db, None)
                attribute_value = apply_conversion_function(
                    raw_value, m.default, m.type
                )
                if (
                    (attribute_value is not None)
                    and (attribute_value != "")
                    and not (m.type in [bool, str, int])
                ):
                    change_record = {
                        "census_data": [],
                        "gsa_fac_data": {},
                        "transformation_function": [],
                    }
                    change_record["census_data"].append(
                        CensusRecord(m.in_db, raw_value).to_dict()
                    )

                    if m.in_dissem == WorkbookFieldInDissem:
                        change_record["gsa_fac_data"] = GsaFacRecord(
                            m.in_sheet, attribute_value
                        ).to_dict()
                        change_record["transformation_function"].append(m.type.__name__)
                    else:
                        change_record["gsa_fac_data"] = GsaFacRecord(
                            m.in_dissem, attribute_value
                        ).to_dict()
                        change_record["transformation_function"].append(m.type.__name__)

                    change_records.append(change_record)

    return change_records
