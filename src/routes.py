from flask import Blueprint, request, jsonify
from analysis import (
    preprocess_data_prophet,
    analyze_stock,
    save_stock_data_to_dynamodb
)
import boto3

routes = Blueprint("routes", __name__)

# Initialize DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
TABLE_NAME = "StockAnalytics"
table = dynamodb.Table(TABLE_NAME)


# Routes for the API
@routes.route("/analyze", methods=["POST"])
def analyze():
    """
    API endpoint to analyze stock data.
    """
    try:
        request_data = request.get_json()

        if not request_data:
            return jsonify({"error": "No data received"}), 400

        stock_name = request_data.get("stock_name")
        stock_data = request_data.get("data")
        years = request_data.get("years", 5)
        forecast_days = request_data.get("forecast_days", 30)
        sell_threshold = request_data.get("sell_threshold", 0.02)
        buy_threshold = request_data.get("buy_threshold", -0.02)
        user_name = request_data.get("user_name")

        df = preprocess_data_prophet(stock_data, years)
        df_a, model_a = analyze_stock(
            df, forecast_days, sell_threshold, buy_threshold
        )
        save_stock_data_to_dynamodb(user_name, stock_name, df_a)

        return jsonify(df_a.to_json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/retrieve_analysis", methods=["POST"])
def retrieve_analysis():
    """
    API endpoint to retrieve stock analysis data.
    """
    try:
        request_details = request.get_json()
        user_name = request_details.get("user_name")
        stock_name = request_details.get("stock_name")

        response = table.query(
            KeyConditionExpression=(
                boto3.dynamodb.conditions.Key('user_name').eq(user_name)
                & boto3.dynamodb.conditions.Key('stock_symbol#date')
                .begins_with(stock_name)
            )
        )

        if 'Items' in response and response['Items']:
            return jsonify(response['Items'])
        return jsonify(
            {"message": "No data found for the given user and stock."}
        ), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def register_routes(app):
    """
    Register the routes with the Flask app.
    """
    app.register_blueprint(routes)
