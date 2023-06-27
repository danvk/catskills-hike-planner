import datetime
import json
import os

import boto3
from SetCoverPy import setcover

from peak_planner import plan_hikes

CACHE_TABLE = os.environ['CACHE_TABLE']
GIT_SHA = os.environ.get('GIT_SHA')
client = boto3.client('dynamodb')


def hello(event, context):
    body = {
        'message': 'Go Serverless v3.0! Your function executed successfully!',
        'input': event,
        'git_sha': GIT_SHA,
    }

    response = {'statusCode': 200, 'body': json.dumps(body)}
    return response


# TODO: input validation / error handling
# TODO: lock down CORS

def find_hikes(event, context):
    params = json.loads(event['body'])
    peaks_needed = params['peaks']
    mode = params.get('mode', 'unrestricted')
    body = {
        'input': event,
        'set-cover-version': setcover.__version__,
        **plan_hikes(peaks_needed, mode),
    }

    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body),
    }

    return response


def get_cache(event):
    response = client.query(
        TableName=CACHE_TABLE,
        Key={
            'gitSha': { 'S': GIT_SHA }
        }
    )
    rows = [{
        k: row.get(k).get('S')
        for k in  ['gitSha', 'requestKey', 'timestamp', 'response']
    } for row in response['Items']]
    response = {'statusCode': 200, 'body': json.dumps(rows)}
    return response


def insert_cache(event):
    params = json.loads(event['body'])
    request_key = params['request_key']
    response = params['response']

    item = {
        'gitSha': {'S': GIT_SHA },
        'requestKey': {'S': request_key },
        'timestamp': {'S': datetime.datetime.utcnow().isoformat() },
        'response': {'S': response },
    }

    resp = client.put_item(
        TableName=CACHE_TABLE,
        Item=item
    )

    response = {'statusCode': 200, 'body': json.dumps({'item': item, 'response': resp})}
    return response
