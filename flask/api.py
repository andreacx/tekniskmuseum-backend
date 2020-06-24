import uuid
import random
import time
import sys
from io import BytesIO
from PIL import Image
from flask import Flask
from flask import request
from flask import jsonify

# Global variables
app = Flask(__name__)
labels = ['cat', 'clock', 'car']
timeLimit = 20


@app.route("/")
def hello():
    return "Hello, World!"


@app.route('/startGame')
def startGame():
    '''
    Starts a new game. A unique token is generated to keep track
    of game. A random label is chosen for the player to draw.
    Startime is recordede to calculate elapsed time when the game ends.
    '''
    startTime = time.time()
    token = uuid.uuid4().hex
    label = random.choice(labels)
    # Insert game detals into DB
    # sql = 'INSERT into games VALUES (%s,%s, %s)'
    # queryParams = (token, label, startTime)
    data = {
        'token': token,
        'label': label,
        'startTime': startTime,
        }
    return jsonify(data), 200


@app.route('/submitAnswer', methods=['POST'])
def submitsolution():
    '''
    Endpoint for user to submit drawing. Drawing is classified with Custom
    Vision.The player wins if the classification is correct and the time
    used is less than the time limit.
    '''
    if 'file' not in request.files:
        return "No image submitted", 400
    image = request.files['file']
    if not allowedFile(image.filename):
        return 'Only png images supported', 415
    classification = classify(image)
    saveImage(image)
    # get game details from DB
    # sql = 'SELECT * FROM game WHERE token=%s'
    # token = request.values['token']
    # queryParam = token
    # mock data
    startTime = time.time()
    label = random.choice(labels)
    # This might be a proble if user has slow connection...
    # Stop time on first line of function instead
    timeUsed = time.time() - startTime
    hasWon = timeUsed < timeLimit and classification == label
    data = {
        'classificaton': classification,
        'hasWon': hasWon,
        'timeUsed': timeUsed,
        }
    return jsonify(data), 200


def classify(image):
    '''
    Classify image with Azure Custom Vision.
    '''
    # TODO: implement custom vision here
    label = random.choice(labels)
    confidence = random.rand()
    return label, confidence


def saveImage(image, label):
    '''
    Save image to azure blob storage. Images are later used to retrain Custom
    Vision classifier.
    '''
    # TODO: implement blob storage upload here
    return


def allowedFile(image):
    '''
    Check if image satisfies the constraints of Custom Vision.
    '''
    # Check if the filename is of PNG type
    png = image.filename.endswith('png')
    # Ensure the file isn't too large
    too_large = len(image.read()) > 4000000
    # Ensure the file has correct resolution
    height, width = Image.open(BytesIO(image.stream.read())).size
    correct_res = (height >= 256) and (width >= 256)
    if not png or too_large or not correct_res:
        return False 
    else:
        return True


if __name__ == '__main__':
    app.run(debug=True)
