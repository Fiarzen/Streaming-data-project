# de-streaming-data-project
An application to retrieve articles from the Guardian API and publish it to a message broker so that it
can be consumed and analysed by other applications.

The tool will accept a search term (e.g. "machine learning"), an optional
"date_from" field, and a reference to a message broker. 
It will use the search
terms to search for articles in the Guardian API. 
It will then post details of up
to ten hits to the message broker.

For example, given the inputs:
• "machine learning"
• "date_from=2023-01-01"
• "guardian_content" it will retrieve all content returned by the API and
post up to the ten most recent items in JSON format onto the
message broker with the ID "guardian_content".


## Configuration

Create a .env file with GUARDIAN_API_KEY="your guardian api key"

run make requirements to install requirements in a venv

### Basic Usage
the example_script.py file can be run to test the application in the command line by typing from the root directory:

python example_script.py 

or for example:
```python
from guardian_api_client import GuardianApiClient

client = GuardianApiClient()

result = client.publish_articles(
    search_term="machine learning",
    date_from="2023-01-01"
)

print(result)
```



### GuardianApiClient


#### `search_articles(search_term, date_from=None, page_size=10, show_fields="bodyText")`
Search for articles in the Guardian API.

- **Parameters:**
  - `search_term`: The term to search for
  - `date_from`: Optional date to filter results from (YYYY-MM-DD format)
  - `page_size`: Number of results to return (default: 10)
  - `show_fields`: Additional fields to include in the response

- **Returns:** Dict containing the API response

#### `process_articles(api_response)`
Process the API response and extract relevant article data.

- **Parameters:**
  - `api_response`: The JSON response from the Guardian API

- **Returns:** List of dictionaries containing processed article data

#### `publish_articles(search_term, broker_reference, date_from=None)`
Search for articles and publish them to the specified message broker.

- **Parameters:**
  - `search_term`: The term to search for
  - `broker_reference`: Reference to the message broker (SQS URL)
  - `date_from`: Optional date to filter results from (YYYY-MM-DD format)

- **Returns:** Dict containing information about the operation

## Message Format

The articles are published to the message broker in the following JSON format:

```json
[
  {
    "webPublicationDate": "2023-11-21T11:11:31Z",
    "webTitle": "Who said what: using machine learning to correctly attribute quotes",
    "webUrl": "https://www.theguardian.com/info/2023/nov/21/who-said-what-using-machine-learning-to-correctly-attribute-quotes",
    "contentPreview": "First 1000 characters of the article content..."
  },
  ...
]
```
## AWS Credentials

To publish messages to AWS services, you need to configure AWS credentials. The library uses boto3, which looks for credentials in the standard locations:
- Environment variables
- Shared credential file (~/.aws/credentials)
- AWS IAM role for EC2/Lambda

### AWS Lambda Function

The package includes a Lambda handler that can be used in AWS Lambda, along with a terraform file that can be used to test the functionality(see bottom of readme for more info)




### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py
```



### Security Scanning

To scan for security vulnerabilities:

```bash
# Install safety
pip install safety

# Run security check
safety scan
```

### Terraform files

If you wish to test the application using terraform to create a lambda function with the application that sends data to an sqs message broker, configure the backend.tf file to a suitable tf state bucket name and region. Additionally, you will need to run make layer-requirements as well as creating an "api_credentials.json" file in the root directory in the form of {"guardian_api_key" :  "your_key_here"}.