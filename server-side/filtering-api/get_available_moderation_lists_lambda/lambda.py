
import json
import os
import boto3
import traceback
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

table = None

def validate_moderation_list(moderation_list):
    if moderation_list['type'].lower() not in ['blacklist', 'whitelist']:
        raise Exception('Invalid moderation list type: ' + moderation_list['type'])


def main_handler(event, context):
    # Get the discourse-provider-id from the query string
    discourse_provider_id = event['queryStringParameters']['discourse-provider-id']

    error_msg = ''
    try:
        # Query the table
        response = table.query(
            KeyConditionExpression=Key('primaryID').eq(discourse_provider_id)
        )
        # Create a list of moderation lists
        moderation_lists = []
        for item in response['Items']:
            moderation_lists.append({
                'id': discourse_provider_id,
                'name': item['name'],
                'type': item['type'],
                'description': item['description'],
                'metadata': item.get('metadata', {})  # Assuming metadata is optional
            })
            validate_moderation_list(moderation_lists[-1])

        # Return the successful response
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'OK', 'lists': moderation_lists})
        }
    except ClientError as e:
        error_msg = e.response['Error']['Message']
        traceback.print_exc()
    except Exception as e:
        error_msg = str(type(e)) + ': ' + str(e)
        traceback.print_exc()
    return {
        'statusCode': 500,
        'body': json.dumps({'status': 'FAILED', 'error_msg': error_msg})
    }


class MockDynamoDBTable:
    def __init__(self,mock_returned_rs):
        self.mock_returned_rs = mock_returned_rs
    def query(self,KeyConditionExpression):
        return {'Items':self.mock_returned_rs}


def local_tasts():
    global table
    event = {
        'queryStringParameters': {
            'discourse-provider-id': '123'
        }
    }
    table = MockDynamoDBTable([])
    res = main_handler(event, None)
    assert res['statusCode'] == 200

    table = MockDynamoDBTable([{}])
    res = main_handler(event, None)
    assert res['statusCode'] == 500

    table = MockDynamoDBTable([{'name':'X','type':'--','description':'Y'}])
    res = main_handler(event, None)
    assert res['statusCode'] == 500

    table = MockDynamoDBTable([{'name': 'X', 'type': 'BlackLIst', 'description': 'Y'}])
    res = main_handler(event, None)
    assert res['statusCode'] == 200

    print ('All tests passed')


LOCAL_ENV = 'HOME' in os.environ and '/Users/' in os.environ['HOME']
if LOCAL_ENV:
    os.environ['TABLE_NAME'] = 'moderation-lists'
else:
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])  # The DynamoDB table name is stored in Lambda environment variables



if __name__ == '__main__':
    local_tasts()

