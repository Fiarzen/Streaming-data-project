"""
Tests for the Lambda handler using pytest.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from src.lambda_handler import lambda_handler





@pytest.fixture
def valid_event():
    """Create a valid test event."""
    return {
        "search_term": "machine learning",
        "date_from": "2023-01-01",
        "broker_reference": "arn:aws:sns:us-east-1:123456789012:guardian_content",
    }


@pytest.fixture
def expected_success_result():
    """Expected success result."""
    return {
        "status": "success",
        "broker_type": "sns",
        "articles_count": 2,
        "message_id": "test-message-id",
    }


@patch("src.lambda_handler.GuardianApiClient")
def test_lambda_handler_success(
    mock_client_class, valid_event, expected_success_result
):
    """Test successful Lambda execution."""
    # Configure mock
    mock_client = MagicMock()
    mock_client.publish_articles.return_value = expected_success_result
    mock_client_class.return_value = mock_client

    # Call handler
    result = lambda_handler(valid_event, {})

    # Verify
    assert result["statusCode"] == 200
    response_body = json.loads(result["body"])
    assert response_body == expected_success_result

    # Check client was called with correct parameters
    mock_client.publish_articles.assert_called_once_with(
        "machine learning",
        "arn:aws:sns:us-east-1:123456789012:guardian_content",
        "2023-01-01",
    )


@patch("src.lambda_handler.GuardianApiClient")
def test_missing_search_term(mock_client_class):
    """Test handling missing search term."""
    # Prepare event with missing search_term
    event = {
        "date_from": "2023-01-01",
        "broker_reference": "arn:aws:sns:us-east-1:123456789012:guardian_content",
    }

    # Call handler
    result = lambda_handler(event, {})

    # Verify
    assert result["statusCode"] == 400
    response_body = json.loads(result["body"])
    assert "error" in response_body
    assert "search_term" in response_body["error"]

    # Ensure client was not created
    mock_client_class.assert_not_called()


@patch("src.lambda_handler.GuardianApiClient")
def test_missing_broker_reference(mock_client_class):
    """Test handling missing broker reference."""
    # Prepare event with missing broker_reference
    event = {"search_term": "machine learning", "date_from": "2023-01-01"}

    # Call handler
    result = lambda_handler(event, {})

    # Verify
    assert result["statusCode"] == 400
    response_body = json.loads(result["body"])
    assert "error" in response_body
    assert "broker_reference" in response_body["error"]


@patch("src.lambda_handler.GuardianApiClient")
def test_validation_error(mock_client_class, valid_event):
    """Test handling validation error from client."""
    # Configure mock to raise ValueError
    mock_client = MagicMock()
    mock_client.publish_articles.side_effect = ValueError("Invalid date format")
    mock_client_class.return_value = mock_client

    # Call handler
    result = lambda_handler(valid_event, {})

    # Verify
    assert result["statusCode"] == 400
    response_body = json.loads(result["body"])
    assert "error" in response_body
    assert response_body["error"] == "Invalid date format"


@patch("src.lambda_handler.GuardianApiClient")
def test_unexpected_error(mock_client_class, valid_event):
    """Test handling unexpected error."""
    # Configure mock to raise Exception
    mock_client = MagicMock()
    mock_client.publish_articles.side_effect = Exception("Unexpected error")
    mock_client_class.return_value = mock_client

    # Call handler
    result = lambda_handler(valid_event, {})

    # Verify
    assert result["statusCode"] == 500
    response_body = json.loads(result["body"])
    assert "error" in response_body
    assert "Unexpected error" in response_body["error"]

@patch("src.lambda_handler.GuardianApiClient")
def test_lambda_handler_invalid_broker(mock_client_class):
    mock_client = MagicMock()
    mock_client.publish_articles.side_effect = ValueError("Unknown broker type")
    mock_client_class.return_value = mock_client

    event = {
        "search_term": "data",
        "broker_reference": "ftp://some-random-broker"
    }

    result = lambda_handler(event, context={})

    assert result["statusCode"] == 400
    assert "Unknown broker type" in json.loads(result["body"])["error"]