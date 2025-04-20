'''Unit Testing for each function in analysis.py
'''
import pytest
import pandas as pd
from analysis import (
    convert_format_with_sentiment,
    preprocess_data_prophet,
    analyze_stock
)


import pytest
import pandas as pd


# Test that valid stock and sentiment events are correctly merged into legacy format
def test_convert_format_valid_stock_and_sentiment_events():
    input_data = {
        "stock_data": {
            "stock_name": "AAPL",
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
                }
            ]
        },
        "sentiment_analysis": {
            "stock_name": "AAPL",
            "events": [
                {
                    "event-type": "stock-sentiment",
                    "attribute": {
                        "score": "0.85",
                        "stock_name": "AAPL"
                    },
                    "time_object": {
                        "time-stamp": "2023-01-01",
                        "time-zone": "GMT+11"
                    }
                }
            ]
        },
        "user_name": "tester",
        "years": 3,
        "forecast_days": 15,
        "sell_threshold": 0.05,
        "buy_threshold": -0.03
    }

    result = convert_format_with_sentiment(input_data)

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
    assert result["data"][0]["Sentiment"] == 0.85

# Test that empty event lists return empty data
def test_convert_format_no_stock_or_sentiment_events():
    input_data = {
        "stock_data": {
            "stock_name": "AAPL",
            "events": []
        },
        "sentiment_analysis": {
            "stock_name": "AAPL",
            "events": []
        },
        "user_name": "tester",
        "years": 3,
        "forecast_days": 15,
        "sell_threshold": 0.05,
        "buy_threshold": -0.03
    }

    legacy_request_data = convert_format_with_sentiment(input_data)

    assert legacy_request_data["data"] == []

# Test that malformed stock events raise an error
def test_convert_format_invalid_stock_format():
    input_data = {
        "stock_data": {
            "events": [
                {
                    "event-type": "stock-ohlc",
                    "attribute": {
                        "close": "145.67"
                        # Missing stock_name key inside attribute
                    }
                }
            ]
        },
        "sentiment_analysis": {
            "events": []
        },
        "user_name": "tester"
    }

    with pytest.raises(Exception) as excinfo:
        convert_format_with_sentiment(input_data)

    assert "'time_object'" in str(excinfo.value) or "'time-stamp'" in str(excinfo.value)

# Test that preprocess_data returns filtered and formatted DataFrame (now including Sentiment)
def test_preprocess_data_prophet_with_sentiment():
    raw = [
        {"Date": "2021-01-01", "Close": 100, "Sentiment": 0.5},
        {"Date": "2024-01-01", "Close": 200, "Sentiment": -0.2}
    ]
    df = preprocess_data_prophet(raw, years=2)

    assert "ds" in df.columns
    assert "y" in df.columns
    assert "sentiment" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["ds"])
    assert all(df["ds"] >= pd.to_datetime("2022-01-01"))

# Test that analyze_stock uses sentiment as regressor and generates forecast
def test_analyze_stock_with_sentiment_regressor():
    raw = [
        {"Date": "2023-01-01", "Close": 100, "Sentiment": 0.5},
        {"Date": "2023-01-02", "Close": 105, "Sentiment": 0.6},
        {"Date": "2023-01-03", "Close": 110, "Sentiment": 0.7},
        {"Date": "2023-01-04", "Close": 115, "Sentiment": 0.8},
        {"Date": "2023-01-05", "Close": 120, "Sentiment": 0.9}
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
