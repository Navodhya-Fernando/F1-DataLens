import http.client
import json
import os
import urllib.parse

def lambda_handler(event, context):
    # Get the exact path and query string from the API Gateway request
    full_path = event.get('rawPath', '')  # e.g., "/rankings/drivers"
    query_string = event.get('rawQueryString', '')  # e.g., "season=2025"
    
    # Set up the connection to the Formula 1 API
    conn = http.client.HTTPSConnection("v1.formula-1.api-sports.io")
    
    headers = {
        'x-rapidapi-host': "v1.formula-1.api-sports.io",
        'x-rapidapi-key': os.environ.get('API_KEY')  # Get key from environment variable
    }
    
    # Build the full path for the external API call
    # The Formula 1 API expects the endpoint path without any prefix
    api_path = full_path
    if query_string:
        api_path = f"{full_path}?{query_string}"
    
    print(f"Making request to: {api_path}")  # This will appear in CloudWatch logs

    # Make the request to the external API
    try:
        conn.request("GET", api_path, headers=headers)
        res = conn.getresponse()
        data = res.read()
        response_body = data.decode("utf-8")
        
        # Parse the response to ensure it's valid JSON
        json_response = json.loads(response_body)
        
        print(f"API response: {json_response}")  # Log the actual response
        
        # Return a successful response to the frontend
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Critical: Allows your S3 website to call this
            },
            'body': json.dumps(json_response)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        # Return an error if something goes wrong
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'requested_path': api_path})
        }