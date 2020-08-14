from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS, cross_origin
import os

# load .env into os.getenv function
loaded = load_dotenv(find_dotenv())

if not loaded:
    raise Exception(".env error")

# now start flask
from flask import Flask
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from clientbot import *
import quiz_api.quiz_api

if __name__ == "__main__":
    app.run(host='localhost', port=9874, debug=True)
