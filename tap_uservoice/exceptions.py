class UservoiceError(Exception):
    """Base class for Uservoice API errors."""

    def __init__(self, message=None, response=None):
        super().__init__(message)
        self.message = message
        self.response = response


class UservoiceBackoffError(UservoiceError):
    """Base class for retryable errors."""

    def __init__(self, message=None, response=None):
        self.response = response

        # Parse Retry-After header, fallback to None
        try:
            self.retry_after = (
                int(response.headers.get('Retry-After'))
                if response and hasattr(response, 'headers')
                and response.headers.get('Retry-After') is not None
                else None
            )
        except (ValueError, TypeError):
            self.retry_after = None

        base_msg = message or "Rate limit hit"
        if self.retry_after is not None:
            base_msg = f"{base_msg} (Retry after {self.retry_after} seconds.)"
        super().__init__(base_msg, response=response)


class UservoiceAuthError(UservoiceError):
    """Raised when authorization with the Uservoice API fails."""
    pass


class UservoiceBadRequestError(UservoiceError):
    """400 status code."""
    pass


class UservoiceUnauthorizedError(UservoiceError):
    """401 status code — triggers re-auth and retry."""
    pass


class UservoiceForbiddenError(UservoiceError):
    """403 status code."""
    pass


class UservoiceNotFoundError(UservoiceError):
    """404 status code."""
    pass


class UservoiceRateLimitError(UservoiceBackoffError):
    """429 status code."""
    pass


class UservoiceInternalServerError(UservoiceBackoffError):
    """500 status code."""
    pass


class UservoiceServiceUnavailableError(UservoiceBackoffError):
    """503 status code."""
    pass


ERROR_CODE_EXCEPTION_MAPPING = {
    400: {
        "raise_exception": UservoiceBadRequestError,
        "message": "A validation exception has occurred.",
    },
    401: {
        "raise_exception": UservoiceUnauthorizedError,
        "message": "Access token is expired or invalid.",
    },
    403: {
        "raise_exception": UservoiceForbiddenError,
        "message": "You do not have permission to access this resource.",
    },
    404: {
        "raise_exception": UservoiceNotFoundError,
        "message": "The resource you have specified cannot be found.",
    },
    429: {
        "raise_exception": UservoiceRateLimitError,
        "message": "API rate limit has been exceeded.",
    },
    500: {
        "raise_exception": UservoiceInternalServerError,
        "message": "The server encountered an unexpected condition.",
    },
    503: {
        "raise_exception": UservoiceServiceUnavailableError,
        "message": "API service is currently unavailable.",
    },
}
