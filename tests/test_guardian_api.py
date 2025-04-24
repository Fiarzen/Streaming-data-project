import pytest
from unittest.mock import patch, MagicMock

from guardian_api import GuardianApiClient

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

@patch('guardian_api_client.requests.get')
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
    call_args = mock_get.call_args[1]['params']
    assert call_args['q'] == "test term"
    assert call_args['api-key'] == "test-api-key"
    assert call_args['from-date'] == "2023-01-01"

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