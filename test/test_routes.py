import pytest
from unittest.mock import patch
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from app import app 

@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    return app.test_client()

@patch("src.routes.preprocess_data_prophet")
@patch("src.routes.analyze_stock")
@patch("src.routes.save_stock_data_to_dynamodb")
def test_analyze_stock(mock_save, mock_analyze, mock_preprocess, client):
    """Test stock analysis API endpoint with realistic mock input."""
    
    # Sample mock DataFrame for preprocessing
    mock_preprocess.return_value = pd.DataFrame({
        "ds": pd.date_range(start="2023-01-01", periods=10),
        "y": [145.32, 146.50, 147.20, 144.80, 143.75, 145.10, 146.95, 148.00, 149.20, 150.30]
    })

    # Mock forecast output
    mock_analyze.return_value = (
        pd.DataFrame({
            "ds": pd.date_range(start="2023-01-11", periods=30),
            "yhat": [151 + i * 0.5 for i in range(30)],  # Simulating a forecast trend
            "yhat_lower": [150 + i * 0.4 for i in range(30)],
            "yhat_upper": [152 + i * 0.6 for i in range(30)],
            "Rolling_Max": [152 + i * 0.6 for i in range(30)],
            "Rolling_Min": [150 + i * 0.4 for i in range(30)],
            "Sell_Signal": [i % 2 == 0 for i in range(30)],  # Alternating sell signals
            "Buy_Signal": [i % 3 == 0 for i in range(30)],  # Buy signals every 3 days
            "Price_Change": [0.02 if i % 2 == 0 else -0.02 for i in range(30)]
        }),
        "mocked_model"
    )

    # Mock save function (DynamoDB interaction)
    mock_save.return_value = None  # No return value expected

    # Simulated API request
    response = client.post("/analyze", json={
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
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    })

    # Assertions
    assert response.status_code == 200
    json_response = response.get_json()

    

@patch("boto3.resource")
def test_retrieve_analysis(mock_boto, client):
    """Test retrieving stock analysis from DynamoDB."""
    mock_table = mock_boto.return_value.Table.return_value
    mock_table.query.return_value = {
        "Items": [
            {
                "stock_symbol": "AAPL",
                "user_name": "test_user",
                "date": "2023-01-01",
                "yhat": "100",
                "yhat_lower": "95",
                "yhat_upper": "105",
                "Rolling_Max": "102",
                "Rolling_Min": "98",
                "Sell_Signal": True,
                "Buy_Signal": False,
                "Price_Change": "0.02",
                "stock_symbol#date": "AAPL#2023-01-01",
            }
        ]
    }

    response = client.post("/retrieve_analysis", json={
        "user_name": "test_user",
        "stock_name": "AAPL"
    })

    assert response.status_code == 200
    response_json = response.json

    # Validate that at least one item contains the expected stock symbol
    assert any(item["stock_symbol"] == "AAPL" for item in response_json)
