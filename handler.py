import datetime
import json
import os

import boto3  # installed by default on AWS
from SetCoverPy import setcover

from peak_planner import plan_hikes

CACHE_TABLE = '' # os.environ['CACHE_TABLE']
GIT_SHA = '' # os.environ.get('GIT_SHA')
# client = boto3.client('dynamodb')
client = None


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


def get_from_cache(request_key: str):
    if not client:
        return None
    resp = client.get_item(
        TableName=CACHE_TABLE,
        Key={'gitShaRequestKey': {'S': GIT_SHA + ' ' + request_key }}
    )
    item = resp.get('Item')
    if not item:
        return None

    return {
        k: item.get(k).get('S')
        for k in  ['gitShaRequestKey', 'gitSha', 'timestamp', 'response']
    }


def insert_in_cache(request_key: str, response: str):
    if not client:
        return
    git_sha_request_key=GIT_SHA + ' ' + request_key

    item = {
        'gitShaRequestKey': {'S': git_sha_request_key },
        'gitSha': {'S': GIT_SHA },
        'timestamp': {'S': datetime.datetime.utcnow().isoformat() },
        'response': {'S': response },
    }

    _resp = client.put_item(
        TableName=CACHE_TABLE,
        Item=item
    )


def find_hikes(event, context):
    params = json.loads(event['body'])
    peaks_needed = params['peaks']
    mode = params.get('mode', 'unrestricted')

    response = None
    computed_hikes = None
    request_key = json.dumps(params)
    response_from_cache = get_from_cache(request_key)
    if response_from_cache:
        response = json.loads(response_from_cache['response'])
        response['cache'] = {
            'hit': True,
            'timestamp': response_from_cache['timestamp'],
            'key': response_from_cache['gitShaRequestKey'],
        }
    else:
        computed_hikes = plan_hikes(peaks_needed, mode)
        response = {
            **computed_hikes,
            'cache': False,
        }

    body = {
        'input': event,
        'set-cover-version': setcover.__version__,
        **response,
    }

    if not response_from_cache:
        insert_in_cache(request_key, json.dumps(computed_hikes))

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body),
    }


def get_cache(event, context):
    response = client.scan(TableName=CACHE_TABLE)
    rows = [{
        k: row.get(k).get('S')
        for k in  ['gitShaRequestKey', 'gitSha', 'timestamp', 'response']
    } for row in response['Items']]
    response = {'statusCode': 200, 'body': json.dumps(rows)}
    return response


def insert_cache(event, context):
    params = json.loads(event['body'])
    request_key = params['request_key']
    response = params['response']
    git_sha_request_key=GIT_SHA + ' ' + request_key

    item = {
        'gitShaRequestKey': {'S': git_sha_request_key },
        'gitSha': {'S': GIT_SHA },
        'timestamp': {'S': datetime.datetime.utcnow().isoformat() },
        'response': {'S': response },
    }

    resp = client.put_item(
        TableName=CACHE_TABLE,
        Item=item
    )

    response = {'statusCode': 200, 'body': json.dumps({'item': item, 'response': resp})}
    return response
