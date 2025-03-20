import pytest
import boto3
from moto import mock_aws
import sys
import os

# Ensure `src` directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from src.app import app  # Import Flask app

@pytest.fixture
def client():
    """Fixture to create a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def mock_dynamodb():
    """Mock DynamoDB using Moto's mock_aws."""
    with mock_aws():
        # ✅ Fix: Set fake AWS credentials to prevent "Unable to locate credentials" error
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        os.environ["AWS_SESSION_TOKEN"] = "test"

        # Initialize a mocked AWS environment
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # ✅ Ensure the table is created before API calls
        table = dynamodb.create_table(
            TableName="StockAnalysis",
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

        table.wait_until_exists()  # ✅ Ensure table exists before using
        yield dynamodb  # Provide the mocked table to tests
