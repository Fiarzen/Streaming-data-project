from src.guardian_api_client import GuardianApiClient
import os
from dotenv import load_dotenv

load_dotenv()


example_client = GuardianApiClient()
response = example_client.search_articles(
    search_term="machine learning", date_from="2023-01-01", show_fields="bodyText"
)

print(response)
