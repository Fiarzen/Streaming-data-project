import pytest
from unittest.mock import patch, MagicMock
from src.guardian_api_client import GuardianApiClient  # adjust import as needed


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