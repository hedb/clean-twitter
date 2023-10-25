
import json
import traceback
from botocore.exceptions import ClientError

from common_src.moderation_lists_util import extract_moderation_lists_from_db

table = None

def main_handler(event, context):
    global table

    # Get the discourse-provider-id from the query string
    discourse_provider_id = event['queryStringParameters']['discourse-provider-id']

    error_msgs = []
    try:
        moderation_lists = extract_moderation_lists_from_db(discourse_provider_id,QA_injected_table=table)

        # Return the successful response
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'OK', 'lists': moderation_lists})
        }
    except ClientError as e:
        error_msgs.append(e.response['Error']['Message'])
        error_msgs.append(traceback.format_exc())
    except Exception as e:
        error_msgs.append(str(type(e)) + ': ' + str(e))
        error_msgs.append(traceback.format_exc())
    return  {
        'statusCode': 500,
        'body': {'status': 'FAILED', 'error_msgs': error_msgs}
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
    if res['statusCode'] != 200:
        for msg in res['body']['error_msgs']:
            for line in msg.split('\n'):
                print (line)

    assert res['statusCode'] == 200
    assert 'error_msgs' not in res['body']

    table = MockDynamoDBTable([{}])
    event['queryStringParameters']['discourse-provider-id'] = '124'
    res = main_handler(event, None)
    assert res['statusCode'] == 500
    assert res['body']['error_msgs'][0] == "<class 'KeyError'>: 'name'"

    table = MockDynamoDBTable([{'name':'X','type':'--','description':'Y'}])
    event['queryStringParameters']['discourse-provider-id'] = '125'
    res = main_handler(event, None)
    assert res['statusCode'] == 500
    assert res['body']['error_msgs'][0] == "<class 'Exception'>: Invalid moderation list type: --"

    table = MockDynamoDBTable([{'name': 'X', 'type': 'BlackLIst', 'description': 'List1'}])
    event['queryStringParameters']['discourse-provider-id'] = '125'
    res = main_handler(event, None)
    assert res['statusCode'] == 200 # the 125 was not save in the cache because of exception. Now it is saved
    assert "List1" in res['body']

    table = MockDynamoDBTable([{'name': 'X', 'type': 'BlackLIst', 'description': 'List2'}])
    event['queryStringParameters']['discourse-provider-id'] = '125'
    res = main_handler(event, None)
    assert res['statusCode'] == 200
    assert "List1" in res['body'] # Now it is saved and we get List1

    print ('All tests passed')





if __name__ == '__main__':
    local_tasts()

