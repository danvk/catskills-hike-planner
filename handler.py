import json

from SetCoverPy import setcover

from peak_planner import plan_hikes

def hello(event, context):
    body = {
        'message': 'Go Serverless v3.0! Your function executed successfully!',
        'input': event,
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
