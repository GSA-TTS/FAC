class SessionExpiredException(Exception):
    def __init__(self, message="Your session has expired. Please log in again."):
        self.message = message
        super().__init__(self.message)

class SessionTimeoutException(Exception):
    def __init__(self, message="Your session is about to expire."):
        self.message = message
        super().__init__(self.message)