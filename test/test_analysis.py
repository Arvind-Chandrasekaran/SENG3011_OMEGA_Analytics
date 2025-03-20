import json
import pytest
from unittest.mock import patch
import sys
import os

# Ensure the module path is correctly set up
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from src.app import app  # noqa: E402


@pytest.fixture
def client():
    """Creates a test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("src.analysis.save_stock_data_to_dynamodb")
def test_analyze(mock_dynamodb, client):
    """
    Test the /analyze endpoint with sample stock data.
    Mocks DynamoDB to avoid actual database writes.
    """
    mock_dynamodb.return_value = None  # Mock database function

    payload = {
        "user_name": "test_user",
        "stock_name": "AAPL",
        "data": [
            {"Date": "2024-01-01", "Close": 150},
            {"Date": "2024-01-02", "Close": 152},
            {"Date": "2024-01-03", "Close": 153},
        ],
        "years": 5,
        "forecast_days": 30,
    }

    response = client.post("/analyze", json=payload)
    assert response.status_code == 200  # Ensure success
    data = json.loads(response.data)
    assert isinstance(data, list)  # Should return a list of predictions


def test_analyze_missing_data(client):
    """
    Test the /analyze endpoint with missing stock data.
    """
    response = client.post("/analyze", json={})
    assert response.status_code == 400  # Expecting a bad request


@patch("src.routes.table.query")
def test_retrieve_analysis(mock_query, client):
    """
    Test the /retrieve_analysis endpoint with mock DynamoDB.
    """
    mock_query.return_value = {
        "Items": [
            {
                "stock_symbol": "AAPL",
                "date": "2024-01-01",
            }
        ]
    }

    payload = {"user_name": "test_user", "stock_name": "AAPL"}
    response = client.post("/retrieve_analysis", json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Should return a list of analysis records


@patch("src.routes.table.query")
def test_retrieve_analysis_no_data(mock_query, client):
    """
    Test /retrieve_analysis when no data exists in DynamoDB.
    """
    mock_query.return_value = {"Items": []}  # Simulating no data

    payload = {"user_name": "fake_user", "stock_name": "AAPL"}
    response = client.post("/retrieve_analysis", json=payload)

    assert response.status_code == 404  # No data found
    data = json.loads(response.data)
    assert "message" in data


def test_invalid_route(client):
    """
    Test accessing a non-existent API endpoint.
    """
    response = client.get("/invalid-route")
    assert response.status_code == 404
