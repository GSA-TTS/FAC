class DataMigrationError(Exception):
    """Exception raised for errors that occur during historic data migration."""

    def __init__(self, message="An error occurred during historic data migration"):
        self.message = message
        super().__init__(self.message)
