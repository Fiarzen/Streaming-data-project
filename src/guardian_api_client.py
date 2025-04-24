
import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

import requests
import boto3


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

class GuardianApiClient:

    API_URL = "https://content.guardianapis.com/search"

    def __init__(self, api_key: Optional[str] = None):

        self.api_key = api_key or os.environ.get("GUARDIAN_API_KEY")
        if not self.api_key:
            raise ValueError("Guardian API key is required. Set GUARDIAN_API_KEY environment variable.")


        self.sns_client = boto3.client('sns')
        self.sqs_client = boto3.client('sqs')

    def search_articles(self, 
                        search_term: str, 
                        date_from: Optional[str] = None, 
                        page_size: int = 10,
                        show_fields: str = "bodyText") -> Dict:
        """
        Search for articles in the Guardian API.
        
        Args:
            search_term: The term to search for
            date_from: Optional date to filter results from (YYYY-MM-DD format)
            page_size: Number of results to return (default: 10)
            show_fields: Additional fields to include in the response
            
        Returns:
            Dict containing the API response
            
        Raises:
            requests.RequestException: If the API request fails
        """
        params = {
            "q": search_term,
            "api-key": self.api_key,
            "page-size": page_size,
            "show-fields": show_fields,
            "order-by": "newest"
        }
        
        if date_from:
            params["from-date"] = date_from
            
        logger.info(f"Searching Guardian API for: {search_term}")
        response = requests.get(self.API_URL, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def process_articles(self, api_response: Dict) -> List[Dict]:
        """
        Process the API response and extract relevant article data.
        
        Args:
            api_response: The JSON response from the Guardian API
            
        Returns:
            List of dictionaries containing processed article data
        """
        try:
            results = api_response.get("response", {}).get("results", [])
            processed_articles = []
            
            for article in results:
                # Extract required fields
                processed_article = {
                    "webPublicationDate": article.get("webPublicationDate"),
                    "webTitle": article.get("webTitle"),
                    "webUrl": article.get("webUrl")
                }
                
                # Add content preview if available
                fields = article.get("fields", {})
                if fields and "bodyText" in fields:
                    body_text = fields["bodyText"]
                    processed_article["contentPreview"] = body_text[:1000] if body_text else None
                    
                processed_articles.append(processed_article)
                
            return processed_articles
        except Exception as e:
            logger.error(f"Error processing articles: {str(e)}")
            raise

    def publish_to_sns(self, topic_arn: str, articles: List[Dict]) -> Dict:
        """
        Publish articles to an SNS topic.
        
        Args:
            topic_arn: The ARN of the SNS topic
            articles: List of article data to publish
            
        Returns:
            Dict containing the SNS publish response
        """
        message = json.dumps(articles)
        logger.info(f"Publishing {len(articles)} articles to SNS topic: {topic_arn}")
        
        response = self.sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            MessageAttributes={
                'TTL': {
                    'DataType': 'Number',
                    'StringValue': '259200'  # 3 days in seconds
                }
            }
        )
        return response    
