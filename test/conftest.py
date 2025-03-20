import pytest
import boto3
from moto import mock_aws
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from src.app import app  

@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def mock_dynamodb():
    """Mock DynamoDB using moto without affecting app.py's real connection."""
    with mock_aws():
        # Create a mock DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")

        # Create the test table
        table = dynamodb.create_table(
            TableName="StockAnalytics",
            KeySchema=[
                {"AttributeName": "user_name", "KeyType": "HASH"},
                {"AttributeName": "stock_symbol#date", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_name", "AttributeType": "S"},
                {"AttributeName": "stock_symbol#date", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )
        table.wait_until_exists()

        yield table  # Provide the mock DB to tests
