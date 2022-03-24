from flask import Flask, jsonify, request
from base64 import b64decode, b64encode
from google.cloud import vision
import numpy as np
import os

app = Flask(__name__, static_folder='build/', static_url_path='/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/hi')
def hi():
    return "hi"

if __name__ == "__main__":
    app.run(debug=True)

