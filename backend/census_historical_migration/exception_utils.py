class DataMigrationError(Exception):
    """Exception raised for errors that occur during historic data migration."""

    def __init__(
        self,
        message="An error occurred during historic data migration",
        tag="",
    ):
        self.message = message
        self.tag = tag
        super().__init__(self.message)


class DataMigrationValueError(DataMigrationError):
    """Exception raised for value errors that occur during historic data migration."""


class CrossValidationError(DataMigrationError):
    """Exception raised for value errors that occur during historic data migration."""
