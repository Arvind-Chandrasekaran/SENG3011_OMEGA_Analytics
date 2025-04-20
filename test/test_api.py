import requests
import pprint

url = "http://127.0.0.1:5001/analyze"  # not the deployed link (for internal testin of the functions)

#data in adage format
data = {
  "stock_data": {
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
    "user_name": "usename99999"
}

response = requests.post(url, json=data)
pprint.pp(response.json())
