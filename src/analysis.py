import pandas as pd
from prophet import Prophet
import requests
import json
from decimal import Decimal
import boto3
import os


DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT")
print("before")
if DYNAMODB_ENDPOINT:
    dynamodb = boto3.resource(
        "dynamodb", region_name="ap-southeast-2", endpoint_url=DYNAMODB_ENDPOINT
    )
    print("hello 11111")
else:
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
    print("hello 222")

TABLE_NAME = "StockAnalytics"
table = dynamodb.Table(TABLE_NAME)


def save_stock_data_to_dynamodb(user_name, stock_symbol, forecast_df):
    """
    Save stock analysis data to DynamoDB.
    """
    for _, row in forecast_df.iterrows():
        item = {
            "user_name": user_name,
            "stock_symbol#date": (
                f"{stock_symbol}#{row['ds'].strftime('%Y-%m-%d')}"  # Composite Key
            ),
            "stock_symbol": stock_symbol,
            "date": row["ds"].strftime("%Y-%m-%d"),
            "yhat": Decimal(str(row["yhat"])),
            "yhat_lower": Decimal(str(row["yhat_lower"])),
            "yhat_upper": Decimal(str(row["yhat_upper"])),
            "Rolling_Max": Decimal(str(row["Rolling_Max"])),
            "Rolling_Min": Decimal(str(row["Rolling_Min"])),
            "Sell_Signal": bool(row["Sell_Signal"]),
            "Buy_Signal": bool(row["Buy_Signal"]),
            "Price_Change": Decimal(str(row["Price_Change"])),
        }
        table.put_item(Item=item)

    print(f"Stock data for {stock_symbol} saved successfully in DynamoDB.")


def preprocess_data_prophet(data, years=5):
    df = pd.DataFrame(data)

    try:
        df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    except Exception as e:
        raise ValueError(f"Error parsing dates: {e}")

    df = df[["Date", "Close", "Sentiment"]].rename(
        columns={"Date": "ds", "Close": "y", "Sentiment": "sentiment"}
    )

    df["ds"] = df["ds"].dt.tz_localize(None)

    cutoff_date = df["ds"].max() - pd.DateOffset(years=years)
    df = df[df["ds"] >= cutoff_date]

    return df


def analyze_stock(df, forecast_days=30, sell_threshold=0.02, buy_threshold=-0.02):
    """
    Train Prophet model on stock data and provide buy/sell recommendations.
    """
    model = Prophet(daily_seasonality=True)

    if "sentiment" in df.columns:
        model.add_regressor("sentiment")

    model.fit(df)

    future = model.make_future_dataframe(periods=forecast_days)

    if "sentiment" in df.columns:
        future = future.merge(df[["ds", "sentiment"]], on="ds", how="left")
        future["sentiment"].fillna(
            method="ffill", inplace=True
        )  # Extend sentiment forward

    forecast = model.predict(future)

    forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    forecast_df["Rolling_Max"] = forecast_df["yhat"].rolling(window=5).max()
    forecast_df["Rolling_Min"] = forecast_df["yhat"].rolling(window=5).min()

    forecast_df["Sell_Signal"] = forecast_df["yhat"] >= forecast_df[
        "Rolling_Max"
    ].shift(1)
    forecast_df["Buy_Signal"] = forecast_df["yhat"] <= forecast_df["Rolling_Min"].shift(
        1
    )

    forecast_df["Price_Change"] = forecast_df["yhat"].pct_change()
    forecast_df["Sell_Signal"] |= forecast_df["Price_Change"] > sell_threshold
    forecast_df["Buy_Signal"] |= forecast_df["Price_Change"] < buy_threshold

    forecast_df = forecast_df.fillna(0)

    return forecast_df, model


def send_results_to_server(callback_url, stock_name, forecast_df, user_name):
    """
    Sends the forecasted stock analysis back to the originating server.
    """
    try:
        data_to_send = {
            "user_name": user_name,
            "stock_name": stock_name,
            "forecast_data": json.loads(forecast_df.to_json(orient="records")),
        }

        response = requests.post(callback_url, json=data_to_send, timeout=10)

        if response.status_code == 200:
            return {
                "message": "Data successfully sent",
                "server_response": response.json(),
            }
        else:
            return {
                "error": f"Failed to send data. Status code: {response.status_code}",
                "server_response": response.text,
            }

    except Exception as e:
        return {"error": str(e)}


def convert_format_with_sentiment(request_data):
    try:
        stock_events = request_data.get("stock_data", {}).get("events", [])
        sentiment_events = request_data.get("sentiment_analysis", {}).get("events", [])

        # Step 1: Parse stock close prices
        stock_data = []
        for event in stock_events:
            if event["event-type"] == "stock-ohlc":
                date = event["time_object"]["time-stamp"]
                close_price = float(event["attribute"]["close"])
                stock_data.append({"Date": date, "Close": round(close_price, 2)})

        # Step 2: Parse sentiment scores
        sentiment_data = {}
        for event in sentiment_events:
            if event["event-type"] == "stock-news":
                date = event["time_object"]["time-stamp"]
                score = float(event["attribute"]["sentiment_score"])
                sentiment_data[date] = round(score, 3)

        # Step 3: Merge sentiment into stock_data
        for entry in stock_data:
            entry["Sentiment"] = sentiment_data.get(
                entry["Date"], 0.0
            )  # default to 0.0

        legacy_request_data = {
            "stock_name": request_data["stock_data"].get("stock_name"),
            "data": stock_data,
            "years": request_data.get("years", 5),
            "forecast_days": request_data.get("forecast_days", 30),
            "sell_threshold": request_data.get("sell_threshold", 0.02),
            "buy_threshold": request_data.get("buy_threshold", -0.02),
            "user_name": request_data.get("user_name"),
        }

        return legacy_request_data

    except Exception as e:
        print("Error in convert_format_with_sentiment:", str(e))
        raise
