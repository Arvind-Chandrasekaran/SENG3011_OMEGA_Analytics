'''This file covers the component testing and integration testing.'''
import pytest
import sys
import os
import boto3

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from app import app  # noqa: E402


@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="function")
def local_dynamodb():
    """Fixture to set up a local DynamoDB table for testing."""
    region = os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2")
    endpoint = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
    dynamodb = boto3.resource("dynamodb", region_name=region, endpoint_url=endpoint)
    table_name = "StockAnalytics"
    try:
        table = dynamodb.Table(table_name)
        table.load()  # Check if table exists
    except Exception:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "user_name", "KeyType": "HASH"},
                {"AttributeName": "stock_symbol#date", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_name", "AttributeType": "S"},
                {"AttributeName": "stock_symbol#date", "AttributeType": "S"}
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        )
        table.wait_until_exists()
    # Clean up any existing items before running a test
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan.get("Items", []):
            batch.delete_item(
                Key={
                    "user_name": each["user_name"],
                    "stock_symbol#date": each["stock_symbol#date"]
                }
            )
    yield table


def test_analyze_stock_success(client, local_dynamodb):
    """Test the /analyze API route with valid stock data."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # Mock input data
    mock_payload = {
        "data_source": "yahoo_finance",
        "dataset_id": (
            "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2"
            "-amazonaws.com"
        ),
        "dataset_type": "Daily stock data",
        "stock_name": "apple",
        "time_object": {
            "timestamp": "2026-03-27 21:03:44.150945",
            "timezone": "GMT+11"
        },
        "events": [
            {
                "attribute": {
                    "close": "244.47000122070312",
                    "stock_name": "apple"
                },
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-18",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {
                    "close": "214.29519653320312",
                    "stock_name": "apple"
                },
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-18",
                    "time-zone": "GMT+11"
                }
            }
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
    assert "ds" in response_data[0]


def test_analyze_stock_missing_fields(client, local_dynamodb):
    """Test the /analyze API with missing required fields."""
    response = client.post("/analyze", json={})
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


def test_analyze_stock_empty_data(client, local_dynamodb):
    """Test the /analyze API with an empty data list."""
    mock_payload = {
        "data_source": "yahoo_finance",
        "dataset_id": (
            "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2"
            "-amazonaws.com"
        ),
        "dataset_type": "Daily stock data",
        "stock_name": "apple",
        "time_object": {
            "timestamp": "2026-03-27 21:03:44.150945",
            "timezone": "GMT+11"
        },
        "events": [],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)

    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


def test_retrieve_analysis_success(client, local_dynamodb):
    """Test retrieving stock analysis from local DynamoDB."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # Put an item directly into the local DynamoDB table
    local_dynamodb.put_item(Item={
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
    assert (
        response_data[0]["analysis_data"]["forecast"]
        == "Mocked Forecast Data"
    )


def test_retrieve_analysis_no_data(client, local_dynamodb):
    """Test retrieving stock analysis when no records exist in local DynamoDB."""
    response = client.post("/retrieve_analysis", json={
        "user_name": "non_existent_user",
        "stock_name": "AAPL"
    })

    assert response.status_code == 404
    response_data = response.get_json()
    assert "message" in response_data
    assert (
        response_data["message"]
        == "No data found for the given user and stock."
    )


def test_retrieve_analysis_invalid_request(client, local_dynamodb):
    """Test /retrieve_analysis API with missing fields in request."""
    response = client.post("/retrieve_analysis", json={})
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


def test_analyze_internal_server_error(client, local_dynamodb, monkeypatch):
    """Test /analyze API when an unexpected exception occurs."""
    def mock_fit(*args, **kwargs):
        raise Exception("Mocked Prophet Training Error")
    monkeypatch.setattr("analysis.Prophet.fit", mock_fit)

    mock_payload = {
        "data_source": "yahoo_finance",
        "dataset_id": (
            "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2"
            "-amazonaws.com"
        ),
        "dataset_type": "Daily stock data",
        "stock_name": "apple",
        "time_object": {
            "timestamp": "2026-03-27 21:03:44.150945",
            "timezone": "GMT+11"
        },
        "events": [
            {
                "attribute": {"close": "244.47000122070312", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-18",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "244.8699951171875", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-19",
                    "time-zone": "GMT+11"
                }
            }
        ],
        "years": 5,
        "forecast_days": 30,
        "sell_threshold": 0.02,
        "buy_threshold": -0.02,
        "user_name": "usename121"
    }

    response = client.post("/analyze", json=mock_payload)
    assert response.status_code == 500
    response_data = response.get_json()
    assert "error" in response_data
    assert "Mocked Prophet Training Error" in response_data["error"]


def test_analyze_invalid_data_format(client, local_dynamodb):
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
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


def test_retrieve_analysis_partial_stock_name(client, local_dynamodb):
    """Ensure partial stock name does not retrieve unrelated data."""
    local_dynamodb.put_item(Item={
        "user_name": "test_user",
        "stock_symbol#date": "AAPL#2024-03-20",
        "analysis_data": {"forecast": "Valid Data"}
    })

    response = client.post("/retrieve_analysis", json={
        "user_name": "test_user",
        "stock_name": "AAP"
    })

    assert response.status_code == 404
    response_data = response.get_json()
    assert "message" in response_data


def test_analyze_missing_user_name(client, local_dynamodb):
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
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data


def test_analyze_insufficient_data(client, local_dynamodb):
    """Test /analyze with too few data points."""
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
    assert response.status_code == 400
    response_data = response.get_json()
    assert "error" in response_data
