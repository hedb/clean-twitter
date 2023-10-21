
import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])  # The DynamoDB table name is stored in Lambda environment variables


def main_handler(event, context):
    # Get the discourse-provider-id from the query string
    discourse_provider_id = event['queryStringParameters']['discourse-provider-id']

    try:
        # Query the table
        response = table.query(
            KeyConditionExpression=Key('primaryID').eq(discourse_provider_id)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({'status': 'FAILED', 'error_msg': e.response['Error']['Message'], 'lists': []})
        }
    else:
        # Create a list of moderation lists
        moderation_lists = []
        for item in response['Items']:
            moderation_lists.append({
                'id': item['id'],
                'name': item['name'],
                'type': item['type'],
                'description': item['description'],
                'metadata': item.get('metadata', {})  # Assuming metadata is optional
            })

        # Return the successful response
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'OK', 'lists': moderation_lists})
        }
