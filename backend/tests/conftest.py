"""
Test configuration for pytest.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Create a test client.
    
    Returns:
        FastAPI test client
    """
    return TestClient(app)
