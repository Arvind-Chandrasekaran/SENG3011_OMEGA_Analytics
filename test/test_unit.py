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
    "data_source": "yahoo_finance",
    "dataset_id": "http://seng3011-omega-25t1-testing-bucket.s3-ap-southeast-2-amazonaws.com",
    "dataset_type": "Daily stock data",
    "stock_name": "honda",
    "time_object": {
      "timestamp": "2026-03-27 21:03:44.150945",
      "timezone": "GMT+11"
    },
    "events": [
      {
        "attribute": {
          "close": "244.47000122070312",
          "stock_name": "honda"
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
          "stock_name": "hinda"
        },
        "event-type": "stock-ohlc",
        "time_object": {
          "duration": "0",
          "duration-unit": "days",
          "time-stamp": "2026-03-18",
          "time-zone": "GMT+11"
        }
      }
    ]
    },
    "sentiment_analysis": {
    "data_source": "yahoo_news",
    "dataset_type": "Financial news",
    "dataset_id": "http://seng3011-omega-news-data.s3-ap-southeast-2-amazonaws.com",
    "time_object": {
    "timestamp": "2025-04-19 22:19:45.990224",
    "timezone": "GMT+11"
    },
    "stock_name": "honda",
    "events": [
    {
      "event-type": "stock-news",
      "attribute": {
        "stock_name": "honda",
        "sentiment_score": "-0.2928",
        "url": "https://finance.yahoo.com/news/detroits-big-three--not-foreign-automakers--are-most-exposed-to-trumps-auto-tariffs-new-report-162635754.html"
      },
      "time_object": {
        "duration": "0",
        "time-stamp": "2025-04-08T16:26:35+00:00",
        "time-zone": "GMT+11",
        "duration-unit": "days"
      }
    },
    {
      "event-type": "stock-news",
      "attribute": {
        "stock_name": "honda",
        "sentiment_score": "0.411",
        "url": "https://finance.yahoo.com/news/foxconn-wants-nissan-evs-strategy-041509641.html"
      },
      "time_object": {
        "duration": "0",
        "time-stamp": "2025-04-09T04:15:09+00:00",
        "time-zone": "GMT+11",
        "duration-unit": "days"
      }
 
    }
        ]
    },
    "years": 5,
    "forecast_days": 30,
    "sell_threshold": 0.02,
    "buy_threshold": -0.02,
    "user_name": "k_sharma"
    }

    result = convert_format_with_sentiment(input_data)

    assert result["stock_name"] == "honda"
    assert result["user_name"] == "k_sharma"
    assert result["years"] == 5
    assert result["forecast_days"] == 30
    assert result["sell_threshold"] == 0.02
    assert result["buy_threshold"] == -0.02
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 2
    assert result["data"][0]["Date"] == "2026-02-18"
    assert result["data"][0]["Close"] == 244.47
    assert result["data"][0]["Sentiment"] == 0.0
    assert result["data"][1]["Date"] == "2026-03-18"
    assert result["data"][1]["Close"] == 214.3
    assert result["data"][1]["Sentiment"] == 0.0
    

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
