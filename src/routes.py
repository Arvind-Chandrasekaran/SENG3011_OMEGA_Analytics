import os
from flask import Blueprint, request, jsonify
from analysis import (
    preprocess_data_prophet,
    analyze_stock,
    save_stock_data_to_dynamodb,
    convert_format_with_sentiment
)
import boto3
from pprint import pprint
from datetime import datetime, timezone
from botocore.exceptions import ClientError

routes = Blueprint("routes", __name__)


DYNAMODB_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT")
print("before")
if DYNAMODB_ENDPOINT:
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2", endpoint_url=DYNAMODB_ENDPOINT)
    print("hello 11111")
else:
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
    print("hello 222")

TABLE_NAME = "StockAnalytics"
table = dynamodb.Table(TABLE_NAME)


# Second dynamoDB table for registering users 
table_users = dynamodb.Table("users") 

SKIP_USER_CHECK = os.environ.get("SKIP_USER_CHECK", "false").lower() == "true"


# Routes for the API
@routes.route("/analyze", methods=["POST"])
def analyze():
    """
    API endpoint to analyze stock data.
    """
    try:
        request_data_new = request.get_json()

        if not request_data_new:
            return jsonify({"error": "No data received"}), 400
       
        
        request_data = convert_format_with_sentiment(request_data_new)

        stock_name = request_data.get("stock_name")
        stock_data = request_data.get("data")
        years = request_data.get("years", 5)
        forecast_days = request_data.get("forecast_days", 30)
        sell_threshold = request_data.get("sell_threshold", 0.02)
        buy_threshold = request_data.get("buy_threshold", -0.02)
        user_name = request_data.get("user_name")

        if not SKIP_USER_CHECK:
            if not user_name:
                return jsonify({"error": "user_name is required"}), 400
        
            if not table_users.get_item(Key={"user_name": user_name}).get("Item"):
                return jsonify({"error": "UserNotRegistered"}), 401
            
        
        
        if (
            not stock_name or not stock_data or not years
            or not forecast_days or not sell_threshold
            or not buy_threshold or not user_name
           ):
            return jsonify({"error": "Missing Field"}), 400

        if len(stock_data) < 2:
            return jsonify({"error": "insufficient data"}), 400

        df = preprocess_data_prophet(stock_data, years)

        df_a, model_a = analyze_stock(
            df, forecast_days, sell_threshold, buy_threshold
        )
        
        
        print("Printing some good stuff:")
        pprint(df_a.to_dict(orient="records"))

        

        save_stock_data_to_dynamodb(user_name, stock_name, df_a)

        return jsonify(df_a.to_dict(orient="records"))

    except Exception as e:
        print("ERROR in /analyze:", str(e))
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

        if not user_name or not stock_name:
            return jsonify({"error": "Missing Field"}), 400
        
        if not SKIP_USER_CHECK:
            if not user_name:
                return jsonify({"error": "user_name is required"}), 400
            if not table_users.get_item(Key={"user_name": user_name}).get("Item"):
                return jsonify({"error": "UserNotRegistered"}), 401
        

        response = table.query(
            KeyConditionExpression=(
                boto3.dynamodb.conditions.Key('user_name').eq(user_name)
                & boto3.dynamodb.conditions.Key('stock_symbol#date')
                .begins_with(stock_name + "#")
            )
        )

        if 'Items' in response and response['Items']:
            return jsonify(response['Items'])
        return jsonify(
            {"message": "No data found for the given user and stock."}
        ), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/register", methods=["POST"])
def register():
    """
    API endpoint to register the a new user to the analytics microservice
    """
    payload   = request.get_json() or {}
    user_name = payload.get("user_name")
    if not user_name:
        return jsonify({"error": "user_name is required"}), 400

    try:
        # 1) Check duplicate
        if table_users.get_item(Key={"user_name": user_name}).get("Item"):
            return jsonify({"error": "UserAlreadyExists"}), 409

        # 2) Write new user
        table_users.put_item(Item={
            "user_name":  user_name
        })
        return jsonify({"message": f"Registered {user_name}"}), 201

    except ClientError:
        return jsonify({"error": "Internal server error"}), 500


def register_routes(app):
    """
    Register the routes with the Flask app.
    """
    app.register_blueprint(routes)


