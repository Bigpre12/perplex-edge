"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing external API calls."""
    client = AsyncMock()
    return client
