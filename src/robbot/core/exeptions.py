class AuthException(Exception):
    """Raised for authentication/authorization related errors."""


class NotFoundException(Exception):
    """Raised when a requested resource is not found."""