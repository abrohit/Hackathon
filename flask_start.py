from dotenv import load_dotenv, find_dotenv
import os

# load .env into os.getenv function
loaded = load_dotenv(find_dotenv())

if not loaded:
    raise Exception(".env error")

# now start flask
from flask import Flask
app = Flask(__name__)

from clientbot import *
import quiz_api.quiz_api

if __name__ == "__main__":
    app.run(host='localhost', port=9874, debug=True)
