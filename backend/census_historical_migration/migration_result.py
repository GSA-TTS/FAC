import copy


class MigrationResult:
    """Stores the result for the current migration"""

    DEFAULT_RESULT = {
        "success": [],
        "errors": [],
        "transformations": [],
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
    def append_transformation(data):
        MigrationResult.result["transformations"].append(data)

    @staticmethod
    def has_errors():
        return len(MigrationResult.result["errors"]) > 0

    @staticmethod
    def append_summary(year, dbkey):
        MigrationResult.result["summaries"][(year, dbkey)] = MigrationResult.result
        # Clear previous results
        MigrationResult.result["success"] = []
        MigrationResult.result["errors"] = []
        MigrationResult.result["transformations"] = []

    @staticmethod
    def get_summaries():
        return MigrationResult.result["summaries"]
