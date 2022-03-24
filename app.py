from flask import Flask, jsonify, request
from base64 import b64decode, b64encode
from google.cloud import vision
import cv2
import numpy as np
import os
import json

app = Flask(__name__, static_folder='build/', static_url_path='/')

#                                HELPER FUNCTIONS
###############################################################################

def convert_to_image(data):
    data_uri = data["data_uri"]
    header, encoded = data_uri.split(",", 1)
    content = b64decode(encoded)

    return content

def detect_text(content):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="bold-mantis-345007-342bdcff7445.json"

    client = vision.ImageAnnotatorClient()
    
    image = vision.Image(content=content)

    response = client.text_detection(
        image=image,
        image_context={"language_hints": ["ko"]})
    
    texts = response.text_annotations

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, flags=cv2.IMREAD_COLOR)

    for text in texts:
        vertices = text.bounding_poly.vertices
        cv2.line(img, (vertices[0].x,vertices[0].y), (vertices[1].x,vertices[1].y), (255,0,0), 2)
        cv2.line(img, (vertices[1].x,vertices[1].y), (vertices[2].x,vertices[2].y), (255,0,0), 2)
        cv2.line(img, (vertices[2].x,vertices[2].y), (vertices[3].x,vertices[3].y), (255,0,0), 2)
        cv2.line(img, (vertices[3].x,vertices[3].y), (vertices[0].x,vertices[0].y), (255,0,0), 2)
    
    cv2.imwrite('savedImage.jpg', img)

    encoded = cv2.imencode('.jpg', img)[1]
    encoded_bytes = encoded.tobytes()
    
    data_uri = "data:image/jpg;base64," + b64encode(encoded_bytes).decode("utf-8")

    return data_uri


###############################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/image_translate', methods=["POST"])
def image_translate():
    data = json.loads(request.data.decode("utf-8") )
    content = convert_to_image(data)

    data_uri = detect_text(content)

    return jsonify({"new_img": data_uri})

if __name__ == "__main__":
    app.run(debug=True)

