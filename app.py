from urllib import response
from flask import Flask, jsonify, request
from base64 import b64decode, b64encode
from requests import post
from google.cloud import vision
import cv2
import numpy as np
import os
import json
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__, static_folder='build/', static_url_path='/')

#                                HELPER FUNCTIONS
###############################################################################

def convert_to_image(data):
    data_uri = data["data_uri"]
    header, encoded = data_uri.split(",", 1)
    content = b64decode(encoded)


    ## Converts the buffer to an array then to a cv2 img
    ## Encode the cv2 image back to np arrary then to buffer
    ## This is to handle the iphone images
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, flags=cv2.IMREAD_COLOR)
    content = cv2.imencode('.jpg', img)[1]
    content = content.tobytes()

    return content

def translate(texts):
    for text in texts:
        0

def detect_language(texts):
    texts_lang = {}

    for text in texts:
        description = text.description
        response = post("https://openapi.naver.com/v1/papago/detectLangs",
            headers = {
                "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
                "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")
                },
            data={
                "query": description
            }).json()
        print(response)
        texts_lang[text.description] = response['langCode']
    
    return texts_lang

def detect_text(content):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="google-credentials.json"

    lang_colors = {
        "en": (255, 255, 255),
        "ko": (0, 255, 255),
        "ja": (255,0,0),
        "zh-CN": (102, 102, 255),
        "zh-TW": (102, 102, 255),
        "vi": (153, 51, 255),
        "id": (255, 255, 153),
        "th": (0, 255, 128),
        "de": (255, 204, 229),
        "ru": (0, 51, 102),
        "es": (102, 178, 255),
        "it": (153, 153, 0),
        "fr": (76, 0, 153)
    }

    client = vision.ImageAnnotatorClient()
    
    image = vision.Image(content=content)

    response = client.text_detection(
        image=image,
        image_context={"language_hints": ["ko"]})
    
    texts = response.text_annotations

    texts_lang = detect_language(texts)

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, flags=cv2.IMREAD_COLOR)

    for text in texts:
        colors = ()
        language = texts_lang[text.description]

        if language in lang_colors:
            color = lang_colors[language]
        else:
            color = (0, 0, 0)


        vertices = text.bounding_poly.vertices
        cv2.line(img, (vertices[0].x,vertices[0].y), (vertices[1].x,vertices[1].y), color, 2)
        cv2.line(img, (vertices[1].x,vertices[1].y), (vertices[2].x,vertices[2].y), color, 2)
        cv2.line(img, (vertices[2].x,vertices[2].y), (vertices[3].x,vertices[3].y), color, 2)
        cv2.line(img, (vertices[3].x,vertices[3].y), (vertices[0].x,vertices[0].y), color, 2)
    
    # cv2.imwrite('savedImage.jpg', img)

    encoded = cv2.imencode('.jpg', img)[1]
    encoded_bytes = encoded.tobytes()
    
    data_uri = "data:image/jpg;base64," + b64encode(encoded_bytes).decode("utf-8")

    return data_uri


###############################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/imagetranslate', methods=["POST"])
def image_translate():
    data = json.loads(request.data.decode("utf-8"))
    content = convert_to_image(data)

    data_uri = detect_text(content)

    return jsonify({"new_img": data_uri})

if __name__ == "__main__":
    app.run(debug=True)

