import pytest
import json
from boto3.dynamodb.conditions import Key
import sys
import os
from moto import mock_aws

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from app import app 

@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@mock_aws
def test_analyze_stock_success(client, mock_dynamodb):
    """Test the /analyze API route with valid stock data."""

    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # Mock input data
    mock_payload = {
        "stock_name": "AAPL",
        "data": [
            {"Date": "2023-01-01", "Close": 145.32},
            {"Date": "2023-01-02", "Close": 146.50},
            {"Date": "2023-01-03", "Close": 147.20},
            {"Date": "2023-01-04", "Close": 144.80},
            {"Date": "2023-01-05", "Close": 143.75},
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)
    
    assert response.status_code == 200
    response_data = response.get_json()
    assert isinstance(response_data, list)
    assert len(response_data) > 0
    assert "ds" in response_data[0]  # Check if forecasted date exists


@mock_aws
def test_analyze_stock_missing_fields(client, mock_dynamodb):
    """Test the /analyze API with missing required fields."""

    response = client.post("/analyze", json={})
    
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_analyze_stock_empty_data(client, mock_dynamodb):
    """Test the /analyze API with an empty data list."""

    mock_payload = {
        "stock_name": "AAPL",
        "data": [],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 400  # Should return bad request due to empty data
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_retrieve_analysis_success(client, mock_dynamodb):
    """Test retrieving stock analysis from mocked DynamoDB."""

    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # Insert mock stock data into the mock DynamoDB
    mock_dynamodb.put_item(Item={
        "user_name": "test_user",
        "stock_symbol#date": "AAPL#2024-03-20",
        "analysis_data": {
            "forecast": "Mocked Forecast Data",
            "buy_signals": [True, False],
            "sell_signals": [False, True]
        }
    })

    response = client.post("/retrieve_analysis", json={
        "user_name": "test_user",
        "stock_name": "AAPL"
    })

    assert response.status_code == 200
    response_data = response.get_json()

    assert isinstance(response_data, list)
    assert len(response_data) > 0
    assert response_data[0]["user_name"] == "test_user"
    assert response_data[0]["analysis_data"]["forecast"] == "Mocked Forecast Data"


@mock_aws
def test_retrieve_analysis_no_data(client, mock_dynamodb):
    """Test retrieving stock analysis when no records exist in DynamoDB."""

    response = client.post("/retrieve_analysis", json={
        "user_name": "non_existent_user",
        "stock_name": "AAPL"
    })

    assert response.status_code == 404
    response_data = response.get_json()
    assert "message" in response_data
    assert response_data["message"] == "No data found for the given user and stock."


@mock_aws
def test_retrieve_analysis_invalid_request(client, mock_dynamodb):
    """Test /retrieve_analysis API with missing fields in request."""

    response = client.post("/retrieve_analysis", json={})

    assert response.status_code == 400  # Should return 400 Bad Request
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_analyze_stock_exception_handling(client, mock_dynamodb, monkeypatch):
    """Test /analyze API when an exception occurs inside the function."""

    def mock_preprocess_data(*args, **kwargs):
        raise Exception("Mocked Exception")

    # Patch the function to simulate an exception
    monkeypatch.setattr("analysis.preprocess_data_prophet", mock_preprocess_data)

    mock_payload = {
        "stock_name": "AAPL",
        "data": [
            {"Date": "2023-01-01", "Close": 145.32}
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 500  # Should return 500 Internal Server Error
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_analyze_invalid_data_format(client, mock_dynamodb):
    """Test /analyze with incorrect data format."""

    mock_payload = {
        "stock_name": "AAPL",
        "data": [
            {"Date": "invalid-date", "Close": "not-a-number"},
            {"Date": "2023-01-02", "Close": 146.50}
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "username123"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_retrieve_analysis_partial_stock_name(client, mock_dynamodb):
    """Ensure partial stock name does not retrieve unrelated data."""

    mock_dynamodb.put_item(Item={
        "user_name": "test_user",
        "stock_symbol#date": "AAPL#2024-03-20",
        "analysis_data": {"forecast": "Valid Data"}
    })

    response = client.post("/retrieve_analysis", json={
        "user_name": "test_user",
        "stock_name": "AAP"  # Partial name
    })

    assert response.status_code == 404  # Should not retrieve "AAPL"
    response_data = response.get_json()
    assert "message" in response_data


@mock_aws
def test_analyze_missing_user_name(client, mock_dynamodb):
    """Test /analyze with missing user_name."""

    mock_payload = {
        "stock_name": "AAPL",
        "data": [
            {"Date": "2023-01-01", "Close": 145.32},
            {"Date": "2023-01-02", "Close": 146.50}
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 400  # Should return bad request
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_analyze_insufficient_data(client, mock_dynamodb):
    """Test /analyze with too few data points (Prophet requires more history)."""

    mock_payload = {
        "stock_name": "AAPL",
        "data": [
            {"Date": "2023-01-01", "Close": 145.32}
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "test_user"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 500  # Should fail because Prophet needs more data
    response_data = response.get_json()
    assert "error" in response_data