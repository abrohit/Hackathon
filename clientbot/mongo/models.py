class User(object):
    def __init__(self, **kwargs):
        # TODO: prevent bad usernames or passwords (too small, etc)
        self.username = kwargs["username"]
        if "password" in kwargs:
            self.password = kwargs["password"]
        self.role = "student"
        if "_id" in kwargs:
            # automatically created by mongo
            self.id = str(kwargs["_id"])
        if "id" in kwargs:
            # automatically created by mongo
            self.id = str(kwargs["id"])
        if "role" in kwargs:
            self.role = kwargs["role"]

    def to_json(self):
        return {"id": str(self.id), "username": str(self.username), "role": self.role}

    def __str__(self):
        return "User(id='%s')" % self.id


class Session(object):
    def __init__(self, **kwargs):
        self.session_id = kwargs["session_id"]
        self.session_name = kwargs["session_name"]
        self.opener = kwargs["opener"]
        self.doubts = kwargs["doubts"]
        self.current_users = kwargs["current_users"]

        # TODO: might display latest doubt?

    def __repr__(self):
        return f"Session <{self.session_id}>"


class Doubt(object):
    def __init__(self, **kwargs):
        self.question = kwargs["question"]
        self.poster = kwargs["poster"]
        self.doubt_id = kwargs["doubt_id"]
        self.comments = kwargs["comments"]
