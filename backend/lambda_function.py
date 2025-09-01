import http.client
import json
import os
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Log the incoming event for debugging
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Extract HTTP method from the event
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        # Handle OPTIONS request for CORS preflight
        if http_method == 'OPTIONS':
            logger.info("Handling OPTIONS preflight request")
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS,POST,PUT,DELETE',
                    'Access-Control-Max-Age': '86400',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'status': 'OK'})
            }
        
        # Get the exact path and query string from the API Gateway request
        full_path = event.get('rawPath', '')
        query_string = event.get('rawQueryString', '')
        
        # Get API key from environment variable
        api_key = os.environ.get('API_KEY')
        if not api_key:
            logger.error("API_KEY environment variable is not set")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Server configuration error'})
            }
        
        # Set up the connection to the Formula 1 API
        conn = http.client.HTTPSConnection("v1.formula-1.api-sports.io")
        
        headers = {
            'x-rapidapi-host': "v1.formula-1.api-sports.io",
            'x-rapidapi-key': api_key
        }
        
        # Build the full path for the external API call
        api_path = full_path
        if query_string:
            api_path = f"{full_path}?{query_string}"
        
        logger.info(f"Making request to external API: {api_path}")

        # Make the request to the external API
        conn.request("GET", api_path, headers=headers)
        res = conn.getresponse()
        data = res.read()
        response_body = data.decode("utf-8")
        
        # Log the response status and size
        logger.info(f"External API response status: {res.status}, size: {len(response_body)} bytes")
        
        # Parse the response to ensure it's valid JSON
        try:
            json_response = json.loads(response_body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid response from data source', 'details': str(e)})
            }
        
        # Return a successful response to the frontend
        return {
            'statusCode': res.status,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'status': 'success',
                'data': json_response
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }