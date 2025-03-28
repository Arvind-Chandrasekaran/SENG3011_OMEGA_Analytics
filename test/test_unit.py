'''Unit Testing for each function in analysis.py
'''
import pytest
import pandas as pd
from analysis import (
    convert_format_,
    preprocess_data_prophet,
    analyze_stock
)


# Test that valid stock events are correctly converted to legacy format
def test_convert_format_valid_stock_events():
    input_data = {
        "stock_name": "AAPL",
        "user_name": "tester",
        "years": 3,
        "forecast_days": 15,
        "sell_threshold": 0.05,
        "buy_threshold": -0.03,
        "events": [
            {
                "event-type": "stock-ohlc",
                "attribute": {
                    "close": "145.67",
                    "stock_name": "AAPL"
                },
                "time_object": {
                    "time-stamp": "2023-01-01",
                    "time-zone": "GMT+11"
                }
            },
            {
                "event-type": "stock news",
                "title": "Ignore this",
                "attributes": {
                    "summary": "Some headline"
                },
                "time_object": {
                    "time-stamp": "2023-01-01T08:00:00"
                }
            }
        ]
    }

    result = convert_format_(input_data)

    assert result["stock_name"] == "AAPL"
    assert result["user_name"] == "tester"
    assert result["years"] == 3
    assert result["forecast_days"] == 15
    assert result["sell_threshold"] == 0.05
    assert result["buy_threshold"] == -0.03
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 1
    assert result["data"][0]["Date"] == "2023-01-01"
    assert result["data"][0]["Close"] == 145.67


# Test that empty event list returns empty data in legacy format
def test_convert_format_no_events():
    input_data = {
        "stock_name": "AAPL",
        "user_name": "tester",
        "years": 3,
        "forecast_days": 15,
        "sell_threshold": 0.05,
        "buy_threshold": -0.03,
        "events": []
    }

    legacy_request_data = convert_format_(input_data)

    assert legacy_request_data["data"] == []


# Test that malformed events raise an error with appropriate missing key
def test_convert_format_invalid_format():
    input_data = {
        "events": [
            {
                "event-type": "stock-ohlc",
                "attribute": {
                    "close": "145.67",
                    "stock_name": "AAPL"
                }
            },
            {
                "event-type": "stock news",
                "title": "Ignore this",
                "attributes": {
                    "summary": "Some headline"
                },
                "time_object": {
                    "time-stamp": "2023-01-01T08:00:00"
                }
            }
        ]
    }

    with pytest.raises(Exception) as excinfo:
        convert_format_(input_data)

    assert str(excinfo.value) in ["'attribute'", "'close'", "'time_object'"]


# Test that preprocessing returns filtered and formatted DataFrame
def test_preprocess_data_prophet_filters_and_formats():
    raw = [
        {"Date": "2021-01-01", "Close": 100},
        {"Date": "2024-01-01", "Close": 200}
    ]
    df = preprocess_data_prophet(raw, years=2)

    assert "ds" in df.columns
    assert "y" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["ds"])
    assert all(df["ds"] >= pd.to_datetime("2022-01-01"))


# Test that Prophet generates a forecast and signal columns correctly
def test_analyze_stock_basic_forecast():
    raw = [
        {"Date": "2023-01-01", "Close": 100},
        {"Date": "2023-01-02", "Close": 105},
        {"Date": "2023-01-03", "Close": 110},
        {"Date": "2023-01-04", "Close": 115},
        {"Date": "2023-01-05", "Close": 120}
    ]
    df = preprocess_data_prophet(raw)
    forecast_df, model = analyze_stock(df, forecast_days=5)

    assert not forecast_df.empty
    assert "ds" in forecast_df.columns
    assert "yhat" in forecast_df.columns
    assert "Buy_Signal" in forecast_df.columns
    assert "Sell_Signal" in forecast_df.columns
    assert "Price_Change" in forecast_df.columns


# save_stock_data_to_dynamodb() function tested with routes
