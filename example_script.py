from src.guardian_api_client import GuardianApiClient
import os
from dotenv import load_dotenv

load_dotenv()

guardian_api_key = os.getenv("GUARDIAN_API_KEY")

if not guardian_api_key:
    GUARDIAN_API_KEY = input("please input your guardian api key")
search_term = input("please input a search_term")
date_from = input("please input a date from")
client = GuardianApiClient(api_key=guardian_api_key)
try:
    results = client.search_articles(search_term, date_from)
    print(results)
except Exception as e:
    print(f"Error occurred: {e}")