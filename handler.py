import json

from SetCoverPy import setcover

def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response


def find_hikes(event, context):
    hikes = json.load(open('data/hikes.json'))
    body = {
        "input": event,
        "num-hikes": len(hikes),
        "set-cover-version": setcover.__version__,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
