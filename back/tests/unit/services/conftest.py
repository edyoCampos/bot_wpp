"""Shared fixtures for unit tests."""

import pytest


@pytest.fixture(name="db_session")
def db_session_alias(db_session_instance):
    """Alias fixture to make db_session available across all test modules."""
    return db_session_instance
