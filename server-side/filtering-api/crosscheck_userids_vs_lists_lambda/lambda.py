import json
import traceback
import os

import boto3
from boto3.dynamodb.conditions import Key

import common_src.moderation_lists_util as moderation_lists_util

dynamodb = boto3.resource('dynamodb')
list_user_mapping_table = dynamodb.Table(os.environ['TABLE_NAME'])
moderation_list_table = None


def isolate_blacklists(discourse_provider_id, id_list):
    moderation_lists = moderation_lists_util.extract_moderation_lists_from_db(discourse_provider_id,
                                                                              QA_injected_table=moderation_list_table)
    filtered_blacklists = [item['list_id'] for item in moderation_lists if
                           item['type'].lower() == 'blacklist' and item['list_id'] in id_list]
    return filtered_blacklists


def main_handler(event, context):
    try:
        global moderation_list_table
        global list_user_mapping

        try:
            body = json.loads(event['body'])
            discourse_provider_id = body['discourse-provider-id']
            user_ids = body['user_ids']
            list_ids = body['list_ids']
        except (KeyError, json.JSONDecodeError, Exception) as e:
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": True
                },
                'body': json.dumps({
                    'status': 'FAILED', 'error_msg': str(e),
                    'excpetion': traceback.format_exc()
                    # 'event': event
                })
            }

        blacklists = isolate_blacklists(discourse_provider_id, list_ids)

        blacklisted_users = []
        for user_id in user_ids:
            response = list_user_mapping_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            if response['Items']:
                if any(item['list_id'] in blacklists for item in response['Items']):
                    blacklisted_users.append(user_id)

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            'body': json.dumps({'status': 'OK', 'blacklisted_users': blacklisted_users})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True
            },
            'body': json.dumps({'status': 'FAILED', 'error_msg': str(e)})
        }


class MockDynamoDBTable:
    def __init__(self, mock_returned_rs):
        self.mock_returned_rs = mock_returned_rs

    def query(self, KeyConditionExpression):
        user_id = KeyConditionExpression._values[1]
        return {'Items': self.mock_returned_rs.get(str(user_id), None)}


def local_tasts():
    global moderation_list_table
    moderation_list_table = moderation_lists_util.MockDynamoDBTable(
        [{'name': 'X', 'list_id': '1', 'type': 'BlackLIst', 'description': 'X'},
         {'name': 'Y', 'list_id': '2', 'type': 'Whitelist', 'description': 'Y'}
         ])
    global list_user_mapping_table

    input_event = {"discourse-provider-id": "1", "user_ids": ["1", "2", "3"], "list_ids": ["1", "2", "3"]}

    list_user_mapping_table = MockDynamoDBTable({})
    res = main_handler(json.dumps(input_event), None)
    assert res['statusCode'] == 200

    list_user_mapping_table = MockDynamoDBTable({'3': [{'list_id': '1', 'user_id': '3'}]})
    res = main_handler(json.dumps(input_event), None)
    assert res['statusCode'] == 200
    assert json.loads(res['body'])['blacklisted_users'] == ['3']

    list_user_mapping_table = MockDynamoDBTable({'3': [{'list_id': '2', 'user_id': '3'}]})
    res = main_handler(json.dumps(input_event), None)
    assert res['statusCode'] == 200
    assert json.loads(res['body'])['blacklisted_users'] == []

    print(' ALl Tests Passed')


LOCAL_ENV = 'HOME' in os.environ and '/Users/' in os.environ['HOME']
if LOCAL_ENV:
    os.environ['TABLE_NAME'] = 'moderation-lists'
else:
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(
        os.environ['TABLE_NAME'])  # The DynamoDB table name is stored in Lambda environment variables

if __name__ == '__main__':
    local_tasts()
