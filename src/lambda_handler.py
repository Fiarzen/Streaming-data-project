"""
Lambda handler for the Guardian API client.

This module provides an AWS Lambda handler that uses the GuardianApiClient 
to search for articles and publish them to a message broker.
"""
import json
import logging
from typing import Dict, Any

from guardian_api_client import GuardianApiClient

# Configure logging
logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: The Lambda event data containing search parameters
        context: The Lambda context
        
    Returns:
        Dict containing the operation response
    """
    try:
        # Extract parameters from the event
        search_term = event.get("search_term")
        date_from = event.get("date_from")
        broker_reference = event.get("broker_reference")
        
        # Validate required inputs
        if not search_term:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "search_term is required"})
            }
            
        if not broker_reference:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "broker_reference is required"})
            }
        
        # Initialize the client and publish articles
        client = GuardianApiClient()
        result = client.publish_articles(search_term, broker_reference, date_from)
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An unexpected error occurred: {str(e)}"})