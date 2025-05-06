
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

                processed_article = {
                    "webPublicationDate": article.get("webPublicationDate"),
                    "webTitle": article.get("webTitle"),
                    "webUrl": article.get("webUrl")
                }
                

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

    def publish_to_sqs(self, queue_url: str, articles: List[Dict]) -> Dict:
        """
        Publish articles to an SQS queue.
        
        Args:
            queue_url: The URL of the SQS queue
            articles: List of article data to publish
            
        Returns:
            Dict containing the SQS send message response
        """
        message = json.dumps(articles)
        logger.info(f"Publishing {len(articles)} articles to SQS queue: {queue_url}")
        
        response = self.sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=message,
            MessageAttributes={
                'TTL': {
                    'DataType': 'Number',
                    'StringValue': '259200'  # 3 days in seconds
                }
            }
        )
        return response
    
    def determine_broker_type(self, broker_reference: str) -> str:
        """
        Determine the type of message broker from the reference.
        
        Args:
            broker_reference: Reference to the message broker
            
        Returns:
            String indicating the broker type ('sns', 'sqs', or 'unknown')
        """
        if broker_reference.startswith("arn:aws:sns:"):
            return "sns"
        elif broker_reference.startswith("https://sqs.") or broker_reference.startswith("http://sqs."):
            return "sqs"
        else:
            return "unknown"
    
    def publish_articles(self, 
                        search_term: str, 
                        broker_reference: str, 
                        date_from: Optional[str] = None) -> Dict:
        """
        Search for articles and publish them to the specified message broker.
        
        Args:
            search_term: The term to search for
            broker_reference: Reference to the message broker (SNS ARN or SQS URL)
            date_from: Optional date to filter results from (YYYY-MM-DD format)
            
        Returns:
            Dict containing information about the operation
            
        Raises:
            ValueError: If the broker type is unknown
        """
        if not search_term:
            raise ValueError("Search term is required")
        if not broker_reference:
            raise ValueError("Broker reference is required")
            

        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date_from format. Use YYYY-MM-DD")
        

        api_response = self.search_articles(search_term, date_from)
        articles = self.process_articles(api_response)
        

        broker_type = self.determine_broker_type(broker_reference)
        
        if broker_type == "sns":
            publish_response = self.publish_to_sns(broker_reference, articles)
            return {
                "status": "success",
                "broker_type": "sns",
                "articles_count": len(articles),
                "message_id": publish_response.get("MessageId")
            }
        elif broker_type == "sqs":
            publish_response = self.publish_to_sqs(broker_reference, articles)
            return {
                "status": "success",
                "broker_type": "sqs",
                "articles_count": len(articles),
                "message_id": publish_response.get("MessageId")
            }
        else:
            raise ValueError(f"Unknown broker type for reference: {broker_reference}")