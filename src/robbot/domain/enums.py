from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
