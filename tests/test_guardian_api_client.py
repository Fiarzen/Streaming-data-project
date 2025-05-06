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
                    }
                },
                {
                    "id": "technology/2023/11/20/article2",
                    "webPublicationDate": "2023-11-20T12:00:00Z",
                    "webTitle": "Test Article 2",
                    "webUrl": "https://www.theguardian.com/test-article-2",
                    "fields": {
                        "bodyText": "This is the body text of test article 2. " * 100
                    }
                }
            ]
        }
    }



@patch("src.guardian_api_client.boto3.client")
def test_init_raises_without_api_key(mock_boto_client, monkeypatch):
    monkeypatch.delenv("GUARDIAN_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Guardian API key is required"):
        GuardianApiClient(api_key=None)


@patch("src.guardian_api_client.requests.get")
@patch("src.guardian_api_client.boto3.client")
def test_search_articles_success(mock_boto_client, mock_requests_get, monkeypatch):
    mock_response = MagicMock()
    expected_json = {"response": {"results": [{"webTitle": "Test Article"}]}}
    mock_response.json.return_value = expected_json
    mock_response.raise_for_status = MagicMock()
    mock_requests_get.return_value = mock_response

    monkeypatch.setenv("GUARDIAN_API_KEY", "fake-api-key")
    client = GuardianApiClient()

    result = client.search_articles("climate change")

    assert result == expected_json
    mock_requests_get.assert_called_once()
    assert mock_requests_get.call_args[1]["params"]["q"] == "climate change"



@patch("src.guardian_api_client.requests.get")
@patch("src.guardian_api_client.boto3.client")
def test_search_articles_with_date(mock_boto_client, mock_requests_get, monkeypatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": {"results": []}}
    mock_response.raise_for_status = MagicMock()
    mock_requests_get.return_value = mock_response

    monkeypatch.setenv("GUARDIAN_API_KEY", "another-fake-key")
    client = GuardianApiClient()

    result = client.search_articles("environment", date_from="2024-01-01")

    assert "from-date" in mock_requests_get.call_args[1]["params"]
    assert mock_requests_get.call_args[1]["params"]["from-date"] == "2024-01-01"
    assert isinstance(result, dict)

def test_process_articles(client, sample_response):
    """Test processing article data from API response."""
    # Call method
    result = client.process_articles(sample_response)
    
    # Verify
    assert len(result) == 2
    assert result[0]['webTitle'] == "Test Article 1"
    assert result[1]['webTitle'] == "Test Article 2"
    
    # Check content preview truncation
    assert len(result[0]['contentPreview']) <= 1000
    assert 'contentPreview' in result[0]

def test_determine_broker_type(client):
    """Test determining broker type from reference."""
    # Test SNS ARN
    assert client.determine_broker_type("arn:aws:sns:us-east-1:123456789012:topic-name") == "sns"
    
    # Test SQS URL
    assert client.determine_broker_type("https://sqs.us-east-1.amazonaws.com/123456789012/queue-name") == "sqs"
    
    # Test unknown
    assert client.determine_broker_type("invalid-reference") == "unknown"


def test_invalid_date_format(client):
    """Test invalid date format."""
    with pytest.raises(ValueError):
        client.publish_articles("test term", "arn:aws:sns:us-east-1:123:topic", "01-01-2023")
