from flask import request, Response
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
import bcrypt
import jwt
import json
import random


from .models import User, Session, Doubt
from flask_start import app
from flask_routes.utilities import jwt_encode, jwt_auth


print("**Creating Mongo Routes... ")

app.config['MONGO_URI'] = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PASS')}@cluster0.8uvh8.mongo" \
                          f"db.net/{os.getenv('MONGO_DB')}?retryWrites=true&w=majority"

mongo = PyMongo(app)


def basic_authenticate(user):
    user_db = mongo.db.users
    existing_user = user_db.find_one({"username": user.username})

    # if username doesn't exist
    if existing_user is None:
        return json.dumps({"success": 0, "error": "Email or Password Incorrect!"}), 401

    existing_user = User(**existing_user)

    # if password matches
    try:
        valid_password = bcrypt.hashpw(user.password.encode('utf-8'), existing_user.password) == \
                         existing_user.password
    except ValueError as e:
        return json.dumps({"success": 0, "error": f"Internal Error: {e}"}), 401

    if not valid_password:
        return json.dumps({"success": 0, "error": "Email or Password Incorrect!"}), 401

    # create jwt
    token = jwt_encode(existing_user.id)

    resp = Response(json.dumps({"success": 1, "response": None}), headers={"Authorization": f"Bearer {token}"})
    return resp


@app.route('/users/current')
def current():
    """ requires auth token """
    user_db = mongo.db.users

    auth = jwt_auth(request.headers)

    if auth is None:
        return json.dumps({"success": 0, "error": "Missing Authorization Header!"}), 401

    auth_user = jwt_auth(request.headers)

    if auth_user["success"] == 0:
        return auth_user, 401

    user_id = jwt_auth(request.headers)["response"]["id"]
    existing_user = user_db.find_one({"_id": ObjectId(user_id)})

    # if username doesn't exist
    if existing_user is None:
        return json.dumps({"success": 0, "error": "Email or Password Incorrect!"}), 401

    existing_user = User(**existing_user)

    return json.dumps({"success": 1, "response": {"user": existing_user.to_json()}})


@app.route('/users/delete')
def delete():
    user_db = mongo.db.users

    auth = jwt_auth(request.headers)
    if auth is not None:
        user_id = jwt_auth(request.headers)["id"]
        existing_user = user_db.find_one({"_id": ObjectId(user_id)})

        # if username doesn't exist
        if existing_user is None:
            return json.dumps({"success": 0, "error": "Email or Password Incorrect!"}), 401

        user_db.delete_one({"_id": ObjectId(user_id)})

        return json.dumps({"success": 1, "response": None})
    return json.dumps({"success": 0, "error": "Missing Authorization Header!"}), 401


@app.route('/users/authenticate', methods=['POST'])
def authenticate():
    content = request.json
    user = User(**content)

    return basic_authenticate(user)


@app.route('/users/register', methods=['POST'])
def register():
    """ Registers if user does not exist. Returns authentication. """
    content = request.json
    user = User(**content)

    user_db = mongo.db.users
    existing_user = user_db.find_one({"username": user.username})

    if existing_user is None:
        hash_pass = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        user_db.insert({
            "username": user.username,
            "password": hash_pass,
            "role": user.role
        })
        return basic_authenticate(user)

    return json.dumps({"status": 0, "error": "User already exists!"}), 401


@app.route('/sessions')
def sessions():
    """ for displaying all available sessions """
    session_db = mongo.db.sessions
    all_sessions = list(session_db.find({}))
    for i, session in enumerate(all_sessions):
        obj = Session(**session)
        all_sessions[i] = {
            "session_id": obj.session_id,
            "session_name": obj.session_name,
            "opener": obj.opener,
            "lobby_size": len(obj.current_users)
        }
    return json.dumps({"success": 1, "response": {"sessions": all_sessions}})


@app.route('/sessions/new', methods=['POST'])
def new_session():
    """ requires auth token. """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    new_id = int(random.random() * 1000000000)
    while session_db.find_one({"session_id": new_id}) is not None:
        # very very unlikely to wind up here but just to be sure
        new_id = int(random.random() * 1000000000)

    content = request.json
    if content is not None and "session_name" in content:
        session_name = content["session_name"]
    else:
        session_name = f"{user.username}'s Session"

    session_db.insert({
        "session_id": new_id,
        "session_name": session_name,
        "opener": user.id,
        "doubts": [],
        "current_users": []
    })

    return json.dumps({"success": 1, "response": {"created": {"session_id": new_id, "session_name": session_name}}})


@app.route('/sessions/get')
def get_session():
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404
    session = Session(**session)
    return json.dumps({"success": 1, "response": {
        "session_id": session.session_id,
        "session_name": session.session_name,
        "opener": session.opener,
        "doubts": session.doubts,
        "current_users": session.current_users
    }})


@app.route('/sessions/enter')
def enter_session():
    """ requires auth token. """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404

    if user.id in session["current_users"]:
        return json.dumps({"success": 0, "error": "User already in session."}), 404

    session_db.update_one({
        "session_id": session_id
    }, {
        "$push": {
            "current_users": user.id
        }
    })

    return json.dumps({"success": 1, "response": None})


@app.route('/sessions/leave')
def leave_session():
    """ requires auth token. """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404

    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User already not in session."}), 404

    session_db.update_one({
        "session_id": session_id
    }, {
        "$pull": {
            "current_users": user.id
        }
    })

    return json.dumps({"success": 1, "response": None})


@app.route('/sessions/delete')
def delete_session():
    """ requires auth token. """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404

    if not session["opener"] == user.id:
        return json.dumps({"success": 0, "error": "Session not opened by current user."}), 404

    session_db.delete_one({"session_id": session_id})
    return json.dumps({"success": 1, "response": None})


@app.route('/doubt/new', methods=['POST'])
def doubt_new():
    """ requires auth token """

    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404

    new_id = int(random.random() * 1000000000)
    while new_id in map(lambda x: x["doubt_id"], session["doubts"]):
        # very very unlikely to wind up here but just to be sure
        new_id = int(random.random() * 1000000000)

    doubt = Doubt(**content, poster=user.id, doubt_id=new_id, comments=[])

    session_db.update_one({
        "session_id": session["session_id"]
    }, {
        "$push": {
            "doubts": {
                "question": doubt.question,
                "comments": doubt.comments,
                "poster": doubt.poster,
                "doubt_id": doubt.doubt_id,
                "upvoters": [doubt.poster],
                "downvoters": []
            }
        }
    })

    return json.dumps({"success": 1, "response": None}), 201


@app.route('/doubt/vote')
def doubt_vote():
    """ requires auth token. for displaying on screen all available doubts """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404
    doubt_id = content["doubt_id"]
    if doubt_id not in map(lambda x: x["doubt_id"], session["doubts"]):
        return json.dumps({"success": 0, "error": "Cannot vote on nonexistent doubt."}), 404
    doubt_idx = list(map(lambda x: x["doubt_id"], session["doubts"])).index(doubt_id)

    typ = content["type"]
    if typ == "upvote":
        if user.id in session["doubts"][doubt_idx]["upvoters"]:
            return json.dumps({"success": 1, "response": "Already upvoted. Did nothing."}), 201
        if user.id not in session["doubts"][doubt_idx]["upvoters"]:
            session["doubts"][doubt_idx]["upvoters"].append(user.id)
        if user.id in session["doubts"][doubt_idx]["downvoters"]:
            session["doubts"][doubt_idx]["downvoters"].remove(user.id)
        session_db.replace_one({"session_id": session_id}, session)
        return json.dumps({"success": 1, "response": "Upvoted."}), 201
    if typ == "neutral":
        if user.id not in session["doubts"][doubt_idx]["upvoters"] and user.id not in session["doubts"][doubt_idx]["downvoters"]:
            return json.dumps({"success": 1, "response": "Already neutral. Did nothing."}), 201
        if user.id in session["doubts"][doubt_idx]["upvoters"]:
            session["doubts"][doubt_idx]["upvoters"].remove(user.id)
        if user.id in session["doubts"][doubt_idx]["downvoters"]:
            session["doubts"][doubt_idx]["downvoters"].remove(user.id)
        session_db.replace_one({"session_id": session_id}, session)
        return json.dumps({"success": 1, "response": "Neutralized."}), 201
    if typ == "downvote":
        if user.id in session["doubts"][doubt_idx]["downvoters"]:
            return json.dumps({"success": 1, "response": "Already downvoted. Did nothing."}), 201
        if user.id not in session["doubts"][doubt_idx]["downvoters"]:
            session["doubts"][doubt_idx]["downvoters"].append(user.id)
        if user.id in session["doubts"][doubt_idx]["upvoters"]:
            session["doubts"][doubt_idx]["upvoters"].remove(user.id)
        session_db.replace_one({"session_id": session_id}, session)
        return json.dumps({"success": 1, "response": "Downvoted."}), 201
    return json.dumps({"success": 0, "error": "\"type\" parameter must be one of [\"upvote\", \"downvote\", \"neutral\"]"}), 404



@app.route('/doubt/resolve')
def resolve():
    """ requires auth token. should only work if called by the user who placed it (or potentially teacher) """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404
    doubt_id = content["doubt_id"]
    if doubt_id not in map(lambda x: x["doubt_id"], session["doubts"]):
        return json.dumps({"success": 0, "error": "Cannot delete nonexistent doubt."}), 404
    doubt_idx = list(map(lambda x: x["doubt_id"], session["doubts"])).index(doubt_id)

    if not session["doubts"][doubt_idx]["poster"] == user.id:
        return json.dumps({"success": 0, "error": "Cannot resolve another user's doubt."}), 404

    session["doubts"].pop(doubt_idx)

    session_db.replace_one({"session_id": session_id}, session)
    return json.dumps({"success": 1, "response": "Deleted doubt."})


@app.route('/doubt/comment', methods=['POST'])
def comment():
    """ requires auth token. comments on the post with a possible solution (with marker for role: student/teacher) """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404
    doubt_id = content["doubt_id"]
    if doubt_id not in map(lambda x: x["doubt_id"], session["doubts"]):
        return json.dumps({"success": 0, "error": "Cannot comment on nonexistent doubt."}), 404
    doubt_idx = list(map(lambda x: x["doubt_id"], session["doubts"])).index(doubt_id)
    comment = content["comment"]

    new_id = int(random.random() * 1000000000)
    while new_id in map(lambda x: x["comment_id"], session["doubts"][doubt_idx]["comments"]):
        # very very unlikely to wind up here but just to be sure
        new_id = int(random.random() * 1000000000)

    session["doubts"][doubt_idx]["comments"].append({
        "comment": comment,
        "commenter": user.id,
        "comment_id": new_id
    })

    session_db.replace_one({"session_id": session_id}, session)
    return json.dumps({"success": 1, "response": "Commented."})


@app.route('/doubt/comment/remove')
def remove_comment():
    """ requires auth token. comments on the post with a possible solution (with marker for role: student/teacher) """
    current_user = current()
    if isinstance(current_user, tuple):
        current_user = current_user[0]  # ignore error type
    if isinstance(current_user, str):
        current_user = json.loads(current_user)  # load up
    if current_user["success"] == 0:
        return current()
    user = User(**(current_user["response"]["user"]))

    session_db = mongo.db.sessions

    content = request.json
    session_id = content["session_id"]
    session = session_db.find_one({"session_id": session_id})
    if session is None:
        return json.dumps({"success": 0, "error": "Session does not exist!"}), 404
    if user.id not in session["current_users"]:
        return json.dumps({"success": 0, "error": "User not yet in session."}), 404
    doubt_id = content["doubt_id"]
    if doubt_id not in map(lambda x: x["doubt_id"], session["doubts"]):
        return json.dumps({"success": 0, "error": "Cannot edit nonexistent doubt."}), 404
    doubt_idx = list(map(lambda x: x["doubt_id"], session["doubts"])).index(doubt_id)
    comment_id = content["comment_id"]
    if comment_id not in map(lambda x: x["comment_id"], session["doubts"][doubt_idx]["comments"]):
        return json.dumps({"success": 0, "error": "Cannot delete nonexistent comment."}), 404
    comment_idx = list(map(lambda x: x["comment_id"], session["doubts"][doubt_idx]["comments"])).index(comment_id)

    if not user.id == session["doubts"][doubt_idx]["comments"][comment_idx]["commenter"] and not session["doubts"][doubt_idx]["poster"] == user.id:
        return json.dumps({"success": 0, "error": "Cannot remove someone else's comments if not commeter or doubter."}), 401

    session["doubts"][doubt_idx]["comments"].pop(comment_idx)

    session_db.replace_one({"session_id": session_id}, session)
    return json.dumps({"success": 1, "response": "Removed Comment."})
