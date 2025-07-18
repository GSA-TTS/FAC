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

    pass


class AdministrativeOverrideError(Exception):
    """
    Exception covering attempts to perform an administrative override
    that is malformed in some way.
    """

    pass
