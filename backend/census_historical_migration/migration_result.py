import copy
from typing import Any


class MigrationResult:
    """Stores the result for the current migration"""

    DEFAULT_RESULT: dict[str, Any] = {
        "success": [],
        "errors": [],
        "summaries": {},
    }
    result = copy.deepcopy(DEFAULT_RESULT)

    @staticmethod
    def reset():
        MigrationResult.result = copy.deepcopy(MigrationResult.DEFAULT_RESULT)

    @staticmethod
    def append_error(data):
        MigrationResult.result["errors"].append(data)

    @staticmethod
    def append_success(data):
        MigrationResult.result["success"].append(data)

    @staticmethod
    def has_errors():
        return len(MigrationResult.result["errors"]) > 0

    @staticmethod
    def append_summary(year, dbkey):
        summary_data = {
            key: value
            for key, value in MigrationResult.result.items()
            if key != "summaries"
        }

        MigrationResult.result["summaries"][(year, dbkey)] = summary_data
        # Clear previous results
        MigrationResult.result["success"] = []
        MigrationResult.result["errors"] = []

    @staticmethod
    def get_summaries():
        return MigrationResult.result["summaries"]
