class ExcelExtractionError(Exception):
    def __init__(
        self,
        message="An error occurred during data extraction from this workbook",
        error_key=None,
    ):
        self.message = message
        self.error_key = error_key
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Key: {self.error_key})"
