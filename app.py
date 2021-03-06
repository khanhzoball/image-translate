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
import detectlanguage
import sys

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


    scale = 3686400/(img.shape[0] * img.shape[1])

    if (scale < 1):
        #calculate the 50 percent of original dimensions
        width = int(img.shape[1] * scale)
        height = int(img.shape[0] * scale)

        # dsize
        dsize = (width, height)

        # resize image
        output = cv2.resize(img, dsize)

        content = cv2.imencode('.jpg', output)[1]
    else:
        content = cv2.imencode('.jpg', img)[1]
    content = content.tobytes()

    return content

def translate(text, language):
    description = text.description

    response = post("https://openapi.naver.com/v1/papago/n2mt",
        headers = {
            "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
            "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")
            },
        data={
            "source": language,
            "target": "en",
            "text": description
        }).json()

    print(response["message"])
    return(response["message"]["result"]["translatedText"])

def detect_language(texts):
    # texts_lang = {}

    # for text in texts:
    #     description = text.description
    #     response = post("https://openapi.naver.com/v1/papago/detectLangs",
    #         headers = {
    #             "X-Naver-Client-Id": os.getenv("NAVER_CLIENT_ID"),
    #             "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET")
    #             },
    #         data={
    #             "query": description
    #         }).json()
    #     print(response)
    #     texts_lang[text.description] = response['langCode']

    # detectlanguage.configuration.api_key = "478af81c74a80fd8caae1d074019e7c8"

    # for text in texts:
    #     description = text.description
    #     response = detectlanguage.detect(description)
    #     if len(response) > 0:
    #         texts_lang[description] = response[0]['language']
    #     else:
    #         texts_lang[description] = "unk"
    #     print(texts_lang[description])
    #     sys.stdout.flush()
    
    # return texts_lang

    return 0

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
    )
    
    texts = response.text_annotations
    language = texts[0].locale

    print("FINISHED GOOGLE VISION DETECTION")
    sys.stdout.flush()

    
    translation = ""
    # texts_lang = detect_language(texts)
    if language == "en":
        translation = texts[0].description
    elif language in lang_colors:
        translation = translate(texts[0], language)
    else:
        translation = "Language not supported"

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, flags=cv2.IMREAD_COLOR)

    for text in texts:
        colors = ()
        # language = texts_lang[text.description]

        # if language in lang_colors:
            # color = lang_colors[language]
        # else:
            # color = (0, 0, 0)


        vertices = text.bounding_poly.vertices
        cv2.line(img, (vertices[0].x,vertices[0].y), (vertices[1].x,vertices[1].y), (255, 0, 0), 2)
        cv2.line(img, (vertices[1].x,vertices[1].y), (vertices[2].x,vertices[2].y), (255, 0, 0), 2)
        cv2.line(img, (vertices[2].x,vertices[2].y), (vertices[3].x,vertices[3].y), (255, 0, 0), 2)
        cv2.line(img, (vertices[3].x,vertices[3].y), (vertices[0].x,vertices[0].y), (255, 0, 0), 2)
        print("DRAWING LINE")
        sys.stdout.flush()
    cv2.imwrite('savedImage.jpg', img)

    encoded = cv2.imencode('.jpg', img)[1]
    encoded_bytes = encoded.tobytes()
    
    data_uri = "data:image/jpg;base64," + b64encode(encoded_bytes).decode("utf-8")

    original_text = texts[0].description.split("\n")
    translated_text = translation.split("\n")

    result = {
        "data_uri": data_uri,
        "original_text": original_text,
        "translated_text": translated_text
    }

    return result


###############################################################################
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/imagetranslate', methods=["POST"])
def image_translate():
    print("RECEIVED DATA URI FROM FRONT END")

    data = json.loads(request.data.decode("utf-8"))
    content = convert_to_image(data)
    print("FINISHED CONVERTING DATA URI TO IMAGE")
    sys.stdout.flush()

    result = detect_text(content)
    print("FINISHED CREATING IMG")
    sys.stdout.flush()

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

