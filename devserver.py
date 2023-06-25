#!/usr/bin/env python
"""Helper for local testing."""

import json

from flask import Flask, request
from flask_cors import CORS

from handler import find_hikes

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/find-hikes', methods=['POST'])
def find_hikes_endpoint():
    body = request.json
    return json.loads(find_hikes({'body': json.dumps(body)}, None)['body'])


app.run(debug=True, host='0.0.0.0')
