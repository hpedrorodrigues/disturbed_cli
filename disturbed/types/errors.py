from typing import Optional


class DisturbedError(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        self.cause = cause
        super(Exception, self).__init__(message)


class DisturbedApiError(DisturbedError):
    def __init__(self, message: str, status_code: int, response_body: str, cause: Optional[Exception] = None):
        msg = f"{message} The server responded with [status_code: {status_code}]: {response_body}."
        super(DisturbedError, self).__init__(msg, cause)
