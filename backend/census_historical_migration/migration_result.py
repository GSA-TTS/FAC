import copy


class MigrationResult:
    """Stores the result for the current migration"""

    DEFAULT_RESULT = {"success": [], "errors": [], "transformations": []}
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
