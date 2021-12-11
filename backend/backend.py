#!/usr/bin/env python3
from flask import Flask, Response, abort, request
from flask_cors import CORS

import os
import requests

from colorize import colorize_image

api = Flask(__name__)
CORS(api)

@api.route('/colorize', methods=['POST'])
def post_image(models={
    'v1': 'colorize_v1',
    'v2': 'colorize_v2'
}):
    version = request.args.get('version')
    if version not in models:
        abort(404, "This model doesn't exist")
    if 'image' not in request.files:
        abort(400, "Please send a file with key=image")
    file = request.files['image']
    colorized_img = colorize_image(file, models[version])

    headers = {}
    if os.getenv("RESTORE_ENABLED", False):
        address = os.getenv("RESTORE_ADDRESS", '127.0.0.1')
        port = os.getenv("RESTORE_PORT", '9002')
        restore = requests.post(f'http://{address}:{port}/restore', files={'image': colorized_img})
        headers={
            'X-Image-Hash': restore.json()['hash'],
            'Access-Control-Expose-Headers': 'X-Image-Hash'
        }

    return Response(
        colorized_img,
        headers=headers,
        mimetype="image/png"
    )

if __name__ == '__main__':
    api.run(host="0.0.0.0")
