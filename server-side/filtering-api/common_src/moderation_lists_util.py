
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from boto3.dynamodb.conditions import Key
import os
import boto3
LOCAL_ENV = 'HOME' in os.environ and '/Users/' in os.environ['HOME']

moderation_list_cache = TTLCache(maxsize=5, ttl=60 * 60)

TABLE_NAME = "moderation-lists"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)  # The DynamoDB table name is stored in Lambda environment variables


def validate_moderation_list(moderation_list):
    if moderation_list['type'].lower() not in ['blacklist', 'whitelist']:
        raise Exception('Invalid moderation list type: ' + moderation_list['type'])


@cached(cache=moderation_list_cache, key =
        lambda discourse_provider_id, QA_injected_table=None: hashkey(discourse_provider_id))
def extract_moderation_lists_from_db(discourse_provider_id, QA_injected_table=None):
    global table

    if QA_injected_table:
        table = QA_injected_table

    response = table.query(
        KeyConditionExpression=Key('primaryID').eq(discourse_provider_id)
    )
    # Create a list of moderation lists
    moderation_lists = []
    for item in response['Items']:
        moderation_lists.append({
            'provider_id': discourse_provider_id,
            'list_id': item['list_id'],
            'name': item['name'],
            'type': item['type'],
            'description': item['description'],
            'metadata': item.get('metadata', {})  # Assuming metadata is optional
        })
        validate_moderation_list(moderation_lists[-1])
    return moderation_lists


class MockDynamoDBTable:
    def __init__(self, mock_returned_rs):
        self.mock_returned_rs = mock_returned_rs

    def query(self, KeyConditionExpression):
        return {'Items': self.mock_returned_rs}
