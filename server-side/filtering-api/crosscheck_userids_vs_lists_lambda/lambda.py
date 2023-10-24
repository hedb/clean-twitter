import os
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




class MockDynamoDBTable:
    def __init__(self,mock_returned_rs):
        self.mock_returned_rs = mock_returned_rs
    def query(self,KeyConditionExpression):
        list_id = KeyConditionExpression._values[0]._values[1]
        user_id = KeyConditionExpression._values[1]._values[1]
        return {'Items':self.mock_returned_rs.get(str(list_id)+'_'+str(user_id),None) }

def local_tasts():
    global table

    table = MockDynamoDBTable({})
    res = lambda_handler({'body':json.dumps({'userIds':['1','2','3'],'listIds':['1','2','3']})},None)
    assert res['statusCode'] == 200

    table = MockDynamoDBTable({'1_3':True})
    res = lambda_handler({'body':json.dumps({'userIds':['1','2','3'],'listIds':['1','2','3']})},None)
    assert res['statusCode'] == 200

    table = MockDynamoDBTable({'1_2': True,'1_3': True})
    res = lambda_handler({'body': json.dumps({'userIds': ['1', '2', '3'], 'listIds': ['1', '2', '3']})}, None)
    assert len(json.loads(res['body'])['list_match'][0]['matches']) == 2

    table = MockDynamoDBTable({'1_2': True, '1_3': True, '1_4': True})
    res = lambda_handler({'body': json.dumps({'userIds': ['1', '2', '3'], 'listIds': ['1', '2', '3']})}, None)
    assert len(json.loads(res['body'])['list_match'][0]['matches']) == 2

    # print(res)
    print(' ALl Tests Passed')





LOCAL_ENV = 'HOME' in os.environ and '/Users/' in os.environ['HOME']
if LOCAL_ENV:
    os.environ['TABLE_NAME'] = 'moderation-lists'
else:
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])  # The DynamoDB table name is stored in Lambda environment variables



if __name__ == '__main__':
    local_tasts()

