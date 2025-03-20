import pytest
import json
import boto3
from moto import mock_aws
from decimal import Decimal
import pandas as pd
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)
from src.app import app  # noqa: E402
from src.analysis import save_stock_data_to_dynamodb  # noqa: E402


TABLE_NAME = "StockAnalytics"


@pytest.fixture
def client():
    """Creates a test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_dynamodb():
    """Mock DynamoDB using moto's mock_aws."""
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")

        # Create a mock DynamoDB table with the correct schema
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "user_name", "KeyType": "HASH"},
                {"AttributeName": "stock_symbol#date", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_name", "AttributeType": "S"},
                {"AttributeName": "stock_symbol#date", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1,
                                   "WriteCapacityUnits": 1},
        )

        # Wait for the table to be active
        table.meta.client.get_waiter("table_exists").wait(TableName=TABLE_NAME)

        yield table  # Provide the table to the test


def test_save_stock_data_to_dynamodb(mock_dynamodb):
    """
    Test saving stock data to DynamoDB using mock_aws.
    """
    user_name = "test_user"
    stock_symbol = "AAPL"

    # Create a sample forecast DataFrame
    data = {
        "ds": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "yhat": [150.5, 151.0],
        "yhat_lower": [148.0, 149.5],
        "yhat_upper": [152.0, 152.5],
        "Rolling_Max": [160, 162],
        "Rolling_Min": [140, 142],
        "Sell_Signal": [True, False],
        "Buy_Signal": [False, True],
        "Price_Change": [1.5, -0.5],
    }
    forecast_df = pd.DataFrame(data)

    # Call the function to save data
    save_stock_data_to_dynamodb(user_name, stock_symbol, forecast_df)

    # Retrieve the inserted data from the mock DynamoDB table
    response = mock_dynamodb.scan()
    items = response["Items"]

    # Ensure data was inserted correctly
    assert len(items) == 2  # Expecting 2 rows in the mock table

    # Check the first record
    assert items[0]["user_name"] == user_name
    assert items[0]["stock_symbol"] == stock_symbol
    assert items[0]["date"] == "2024-01-01"
    assert items[0]["yhat"] == Decimal("150.5")
    assert items[0]["Sell_Signal"] is True
    assert items[0]["Buy_Signal"] is False


def test_analyze(client, mock_dynamodb):
    """
    Test the /analyze endpoint with sample stock data.
    """
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

    # Verify data was inserted into mock DynamoDB
    result = mock_dynamodb.scan()
    assert len(result["Items"]) > 0  # Ensure at least one item was inserted


def test_retrieve_analysis(client, mock_dynamodb):
    """
    Test the /retrieve_analysis endpoint with mock DynamoDB.
    """
    # Insert a mock record into the DynamoDB table
    mock_dynamodb.put_item(
        Item={
            "user_name": "test_user",
            "stock_symbol#date": "AAPL#2024-01-01",
            "stock_symbol": "AAPL",
            "date": "2024-01-01",
            "forecast": [155, 157, 160],
        }
    )

    payload = {"user_name": "test_user", "stock_name": "AAPL"}
    response = client.post("/retrieve_analysis", json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)

    # Ensure response is a list and contains expected data
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["stock_symbol"] == "AAPL"


def test_retrieve_analysis_no_data(client, mock_dynamodb):
    """
    Test /retrieve_analysis when no data exists in DynamoDB.
    """
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
