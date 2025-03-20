import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from app import app 

@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.config["TESTING"] = True
    client = app.test_client()
    yield client

def test_app_running(client):
    """Test if the Flask app is running."""
    response = client.get("/")
    assert response.status_code == 404  # Root route is not defined
