
from cachetools import cached, TTLCache
from cachetools.keys import hashkey
from boto3.dynamodb.conditions import Key

moderation_list_cache = TTLCache(maxsize=5, ttl=60*60)

def validate_moderation_list(moderation_list):
    if moderation_list['type'].lower() not in ['blacklist', 'whitelist']:
        raise Exception('Invalid moderation list type: ' + moderation_list['type'])


@cached(cache=moderation_list_cache, key=lambda x,y: hashkey(y))
def extract_moderation_lists_from_db(table, discourse_provider_id):
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
    return moderation_lists
