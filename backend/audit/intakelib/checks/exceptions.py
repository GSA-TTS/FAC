class CheckIRError(Exception):
    def __init__(
        self,
        message="If you see this validation error, please contact the helpdesk and include your workbook(s).",
        error_location="Unknown location",
    ):
        self.message = message
        self.error_location = error_location
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Location: {self.error_location})"
