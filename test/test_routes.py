import pytest
import sys
import os
from moto import mock_aws


sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src")
    )
)

from app import app  # noqa: E402


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
    mock_payload =  {
        "data_source": "yahoo_finance",
        "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
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
            },
            {
                "attribute": {"close": "245.8300018310547", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-20",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "245.5500030517578", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-21",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "247.10000610351562", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-24",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "247.0399932861328", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-25",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "240.36000061035156", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-26",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "237.3000030517578", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-27",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "241.83999633789062", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-02-28",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "238.02999877929688", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-03",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "235.92999267578125", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-04",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "235.74000549316406", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-05",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "235.3300018310547", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-06",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "239.07000732421875", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-07",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "227.47999572753906", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-10",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "220.83999633789062", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-11",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "216.97999572753906", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-12",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "209.67999267578125", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-13",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "213.49000549316406", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-14",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "214.0", "stock_name": "apple"},
                "event-type": "stock-ohlc",
                "time_object": {
                    "duration": "0",
                    "duration-unit": "days",
                    "time-stamp": "2026-03-17",
                    "time-zone": "GMT+11"
                }
            },
            {
                "attribute": {"close": "214.29519653320312", "stock_name": "apple"},
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

    mock_payload =  {
        "data_source": "yahoo_finance",
        "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
        "dataset_type": "Daily stock data",
        "stock_name": "apple",
        "time_object": {
            "timestamp": "2026-03-27 21:03:44.150945",
            "timezone": "GMT+11"
        },
        "events": [
            
        ],
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
    assert (
            response_data[0]["analysis_data"]["forecast"]
            == "Mocked Forecast Data"
           )


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
    assert (
            response_data["message"]
            == "No data found for the given user and stock."
           )


@mock_aws
def test_retrieve_analysis_invalid_request(client, mock_dynamodb):
    """Test /retrieve_analysis API with missing fields in request."""

    response = client.post("/retrieve_analysis", json={})

    assert response.status_code == 400  # Should return 400 Bad Request
    response_data = response.get_json()
    assert "error" in response_data


@mock_aws
def test_analyze_internal_server_error(client, mock_dynamodb, monkeypatch):
    """Test /analyze API when an unexpected exception occurs."""

    # Force an exception inside Prophet by mocking the model training function
    def mock_fit(*args, **kwargs):
        raise Exception("Mocked Prophet Training Error")

    # Monkeypatch the Prophet `fit` method to simulate a failure
    monkeypatch.setattr("analysis.Prophet.fit", mock_fit)

    mock_payload = {
        "data_source": "yahoo_finance",
        "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
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

    assert response.status_code == 500  # Should return Internal Server Error
    response_data = response.get_json()
    assert "error" in response_data
    assert "Mocked Prophet Training Error" in response_data["error"]


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

    assert response.status_code == 400
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
