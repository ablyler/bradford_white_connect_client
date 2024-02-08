class BradfordWhiteConnectAuthenticationError(Exception):
    """Raised when authentication fails.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Authentication failed."):
        self.message = message
        super().__init__(self.message)


class BradfordWhiteConnectUnknownException(Exception):
    """Raised when an unknown error occurs"""

    def __init__(self, status):
        """Initialize exception"""
        super(BradfordWhiteConnectUnknownException, self).__init__(status)
        self.status = status
