from dotenv import load_dotenv, find_dotenv

# load .env into os.getenv function
loaded = load_dotenv(find_dotenv())

if not loaded:
    raise Exception(".env error")

# now start flask
from flask import Flask
app = Flask(__name__)

import clientbot.routes

app.run()
# app.run(host='localhost', port=9874, debug=True)
