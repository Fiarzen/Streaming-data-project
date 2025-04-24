# de-streaming-data-project
An application to retrieve
articles from the Guardian API and publish it to a message broker so that it
can be consumed and analysed by other applications.
The tool will accept a search term (e.g. "machine learning"), an optional
"date_from" field, and a reference to a message broker. It will use the search
terms to search for articles in the Guardian API. It will then post details of up
to ten hits to the message broker.
For example, given the inputs:
• "machine learning"
• "date_from=2023-01-01"
• "guardian_content" it will retrieve all content returned by the API and
post up to the ten most recent items in JSON format onto the
message broker with the ID "guardian_content".