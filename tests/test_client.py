import pytest
from unittest.mock import patch, MagicMock

from src.guardian_api_client import GuardianApiClient


@pytest.fixture
def client():
    """Create a test client instance."""
    return GuardianApiClient(api_key="test-api-key")


@pytest.fixture
def sample_response():
    """Sample API response for testing."""
    return {
        "response": {
            "status": "ok",
            "userTier": "developer",
            "total": 2,
            "results": [
                {
                    "id": "technology/2023/11/21/article1",
                    "webPublicationDate": "2023-11-21T12:00:00Z",
                    "webTitle": "Test Article 1",
                    "webUrl": "https://www.theguardian.com/test-article-1",
                    "fields": {
                        "bodyText": "This is the body text of test article 1. " * 100
                    },
                },
                {
                    "id": "technology/2023/11/20/article2",
                    "webPublicationDate": "2023-11-20T12:00:00Z",
                    "webTitle": "Test Article 2",
                    "webUrl": "https://www.theguardian.com/test-article-2",
                    "fields": {
                        "bodyText": "This is the body text of test article 2. " * 100
                    },
                },
            ],
        }
    }


@patch("src.guardian_api_client.requests.get")
def test_search_articles(mock_get, client, sample_response):
    """Test searching articles from the Guardian API."""
    # Configure mock
    mock_response = MagicMock()
    mock_response.json.return_value = sample_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call method
    result = client.search_articles("test term", "2023-01-01")

    # Verify
    mock_get.assert_called_once()
    assert result == sample_response

    # Check correct parameters were used
    call_args = mock_get.call_args[1]["params"]
    assert call_args["q"] == '"test term"'
    assert call_args["api-key"] == "test-api-key"
    assert call_args["from-date"] == "2023-01-01"


def test_process_articles(client, sample_response):
    """Test processing article data from API response."""
    # Call method
    result = client.process_articles(sample_response)

    # Verify
    assert len(result) == 2
    assert result[0]["webTitle"] == "Test Article 1"
    assert result[1]["webTitle"] == "Test Article 2"

    # Check content preview truncation
    assert len(result[0]["contentPreview"]) <= 1000
    assert "contentPreview" in result[0]


def test_determine_broker_type(client):
    """Test determining broker type from reference."""
    # Test SNS ARN
    assert (
        client.determine_broker_type("arn:aws:sns:us-east-1:123456789012:topic-name")
        == "sns"
    )

    # Test SQS URL
    assert (
        client.determine_broker_type(
            "https://sqs.us-east-1.amazonaws.com/123456789012/queue-name"
        )
        == "sqs"
    )

    # Test unknown
    assert client.determine_broker_type("invalid-reference") == "unknown"


@patch("src.guardian_api_client.GuardianApiClient.search_articles")
@patch("src.guardian_api_client.GuardianApiClient.process_articles")
@patch("src.guardian_api_client.GuardianApiClient.publish_to_sns")
def test_publish_articles_sns(
    mock_publish_sns, mock_process, mock_search, client, sample_response
):
    """Test publishing articles to SNS."""
    # Configure mocks
    mock_search.return_value = sample_response
    mock_process.return_value = [
        {
            "webPublicationDate": "2023-11-21T12:00:00Z",
            "webTitle": "Test Article 1",
            "webUrl": "https://www.theguardian.com/test-article-1",
            "contentPreview": "This is a preview...",
        }
    ]
    mock_publish_sns.return_value = {"MessageId": "test-message-id"}

    # Call method
    result = client.publish_articles(
        "test term", "arn:aws:sns:us-east-1:123456789012:topic-name", "2023-01-01"
    )

    # Verify
    mock_search.assert_called_once()
    mock_process.assert_called_once()
    mock_publish_sns.assert_called_once()
    assert result["status"] == "success"
    assert result["broker_type"] == "sns"
    assert result["message_id"] == "test-message-id"


@patch("src.guardian_api_client.GuardianApiClient.search_articles")
@patch("src.guardian_api_client.GuardianApiClient.process_articles")
@patch("src.guardian_api_client.GuardianApiClient.publish_to_sqs")
def test_publish_articles_sqs(
    mock_publish_sqs, mock_process, mock_search, client, sample_response
):
    """Test publishing articles to SQS."""
    # Configure mocks
    mock_search.return_value = sample_response
    mock_process.return_value = [
        {
            "webPublicationDate": "2023-11-21T12:00:00Z",
            "webTitle": "Test Article 1",
            "webUrl": "https://www.theguardian.com/test-article-1",
            "contentPreview": "This is a preview...",
        }
    ]
    mock_publish_sqs.return_value = {"MessageId": "test-message-id"}

    # Call method
    result = client.publish_articles(
        "test term",
        "https://sqs.us-east-1.amazonaws.com/123456789012/queue-name",
        "2023-01-01",
    )

    # Verify
    mock_search.assert_called_once()
    mock_process.assert_called_once()
    mock_publish_sqs.assert_called_once()
    assert result["status"] == "success"
    assert result["broker_type"] == "sqs"
    assert result["message_id"] == "test-message-id"


def test_invalid_date_format(client):
    """Test invalid date format."""
    with pytest.raises(ValueError):
        client.publish_articles(
            "test term", "arn:aws:sns:us-east-1:123:topic", "01-01-2023"
        )
