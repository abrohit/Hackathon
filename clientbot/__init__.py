from dotenv import load_dotenv, find_dotenv
import os

# load .env into os.getenv function
loaded = load_dotenv(find_dotenv())

if not loaded:
    raise Exception(".env error")

# now start flask
from flask import Flask
app = Flask(__name__)

import clientbot.routes

if __name__ is "__main__":
    port = int(os.environ.get('PORT', 9874))
    app.run(host="0.0.0.0", port=port)
    # app.run(host='localhost', port=9874, debug=True)
