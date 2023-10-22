import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('moderation_lists')  # assuming this is your table name


def lambda_handler(event, context):
    # Parse the JSON input to get the lists of user IDs and list IDs
    try:
        body = json.loads(event['body'])
        user_ids = body['userIds']
        list_ids = body['listIds']
    except KeyError or json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'status': 'FAILED', 'error_msg': 'Invalid input format'})
        }

    list_match = []
    for list_id in list_ids:
        matches = []
        for user_id in user_ids:
            response = table.query(
                KeyConditionExpression=Key('listId').eq(list_id) & Key('userId').eq(user_id)
            )
            if response['Items']:
                matches.append(user_id)

        if matches:
            list_match.append({
                'list_id': list_id,
                'matches': matches
            })

    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'OK', 'list_match': list_match})
    }
