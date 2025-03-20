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
def test_analyze_stock(client, mock_dynamodb):
    """Test the /analyze API route without real DynamoDB connection."""

    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # dynamodb = mock_dynamodb
    # table = dynamodb.Table("StockAnalysis")
        
    # Mock input data
    mock_payload = {
        "stock_name": "AAPL",
        "data": [
                {"Date": "2023-01-01", "Close": 145.32},
                {"Date": "2023-01-02", "Close": 146.50},
                {"Date": "2023-01-03", "Close": 147.20},
                {"Date": "2023-01-04", "Close": 144.80},
                {"Date": "2023-01-05", "Close": 143.75},
                {"Date": "2023-01-06", "Close": 145.10},
                {"Date": "2023-01-07", "Close": 146.95},
                {"Date": "2023-01-08", "Close": 148.00},
                {"Date": "2023-01-09", "Close": 149.20},
                {"Date": "2023-01-10", "Close": 150.30}
            ]
        ,
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 200
    response_data = response.get_json()
    # assert "forecast" in response_data
    # assert "stock_name" in response_data
    # assert response_data["stock_name"] == "AAPL"

@mock_aws
def test_retrieve_analysis(client, mock_dynamodb):
    """Test retrieving stock analysis from mocked DynamoDB."""

    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    
    # Get mock DynamoDB instance & table
    # dynamodb = mock_dynamodb
    # table = dynamodb.Table("StockAnalysis")

    # Insert test stock data
    mock_dynamodb.put_item(Item={
        "user_name": "test_user",
        "stock_symbol#date": "AAPL#2024-03-20",
        "analysis_data": {
            "forecast": "Mocked Forecast Data",
            "buy_signals": [True, False],
            "sell_signals": [False, True]
        }
    })

    # Call API to retrieve stored analysis
    response = client.post("/retrieve_analysis", json={
        "user_name": "test_user",
        "stock_name": "AAPL"
    })

    assert response.status_code == 200
    response_data = response.get_json()

    assert isinstance(response_data, list)  # Ensure response is a list
    assert len(response_data) > 0  # Ensure at least one record is returned
    assert response_data[0]["user_name"] == "test_user"
    assert response_data[0]["analysis_data"]["forecast"] == "Mocked Forecast Data"
