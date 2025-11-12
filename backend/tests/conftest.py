"""Pytest configuration and fixtures for testing"""

import os
import sys
from unittest.mock import patch
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"  # File-based SQLite for tests


@pytest.fixture(scope="session", autouse=True)
def mock_pytorch_model():
    """
    Mock the PyTorch model loading to make tests fast
    This prevents loading the 78MB model checkpoint during test
    """

    # Import Generator to get its structure
    from models import Generator
    import torch

    # Create a real generator to get the proper state_dict structure
    temp_gen = Generator(ngpu=0)
    real_state_dict = temp_gen.state_dict()

    # Mock torch.load to return a proper checkpoint with real keys but zero values
    with patch('torch.load') as mock_load:
        mock_load.return_value = {'generator_state_dict': real_state_dict}
        yield


@pytest.fixture
def client():
    """Create a test client for the FastAPI app.

    The TestClient context manager automatically triggers the app lifespan,
    which calls init_db() to create tables.
    """
    from fastapi.testclient import TestClient
    from app import app
    from database import Base, engine

    # Clean slate before starting
    Base.metadata.drop_all(bind=engine)

    # Create and return test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up: drop all tables after tests
    Base.metadata.drop_all(bind=engine)
