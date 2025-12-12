class AuthException(Exception):
    """Raised for authentication/authorization related errors."""


class NotFoundException(Exception):
    """Raised when a requested resource is not found."""


class ExternalServiceError(Exception):
    """Raised when an external service (e.g., WAHA API) returns an error."""
