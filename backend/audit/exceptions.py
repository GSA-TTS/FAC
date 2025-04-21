class SessionExpiredException(Exception):
    def __init__(self, message="Your session has expired. Please log in again."):
        self.message = message
        super().__init__(self.message)


class SessionWarningException(Exception):
    def __init__(self, message="Your session is about to expire."):
        self.message = message
        super().__init__(self.message)


class LateChangeError(Exception):
    """
    Exception covering attempts to change submissions that don't have the in_progress
    status.
    """


class VersionMismatchException(Exception):
    """
    Exception covering when the version of the Audit is not what is expected.
    """

    def __init__(self, expected, actual):
        self.message = f"Version Mismatch: Expected {expected} Got {actual}"
        super().__init__(self.message)
