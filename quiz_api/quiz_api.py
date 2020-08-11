from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# API INSTRUCTIONS:
# The way data is collected/stored is a little weird. First off, to get and post data you need a lecture id and a question number. The lecture id is the teacher's
# username + the lecture number. So for a lecturer with username Skola to post his first lecture's second question, he would use the endpoint
# question/Skola1/2, with Skola1 being the lecture id.
# When posting data you need to specify 'q_type', or question type. This will either be 'mc' for multiple choice(including true/false) or 'frq' for free response.
# For the 'question' field you just need to write out the quesiton.
# The correct answer would be stored under 'correct', for an frq, input N/A for this field.
# For ease of storing in the database, all the wrong answers are stored in one string with each answer being seperated by a double space. To break up
# the answers after a get request you would probably need to use something like ".split('  ')". For frq's just write in N/A.
# The session_id is a classifier to determine which session the question belongs to.
# The FRQ get and post methods are very similar, but they also require the students username.
# For examples of the data needed as well as example get and post requests look at test.py.

class QuizModel(db.Model):
    unique_id = db.Column(db.String(50), primary_key = True)
    lecture_id = db.Column(db.String(50), nullable = False)
    question_num = db.Column(db.Integer, nullable = False)
    question = db.Column(db.String(500), nullable = False)
    session_id = db.Column(db.String(225), nullable = False)
    q_type = db.Column(db.String(5), nullable = False)
    correct = db.Column(db.String(500), nullable = False)
    wrong = db.Column(db.String(1500), nullable = False)

class FRQModel(db.Model):
    unique_id = db.Column(db.String(100), primary_key = True)
    lecture_id = db.Column(db.String(50), nullable = False)
    question_num = db.Column(db.Integer, nullable = False)
    student_name = db.Column(db.String(50), nullable = False)
    response = db.Column(db.String(3000), nullable = False)
    session_id = db.Column(db.String(225), nullable = False)

questionPostArgs = reqparse.RequestParser()
questionPostArgs.add_argument("question", type=str, help="Need a question!", required = True)
questionPostArgs.add_argument("q_type", type=str, help="Is it mc or frq?", required = True)
questionPostArgs.add_argument("correct", type=str, help="Need a correct answer! If frq just write N/A", required = True)
questionPostArgs.add_argument("wrong", type=str, help="Put some wrong answers seperated by a space. For frq write N/A", required = True)
questionPostArgs.add_argument("session_id", type=str, help="Enter the session id", required = True)

FRQArgs = reqparse.RequestParser()
FRQArgs.add_argument("response", type=str, help="Enter the student's response", required = True)
FRQArgs.add_argument("session_id", type=str, help="Enter the session id", required = True)



question_fields = {
    "unique_id" : fields.String,
    "lecture_id" : fields.String,
    "question_num" : fields.Integer,
    "session_id" : fields.String,
    "question" : fields.String,
    "q_type" : fields.String,
    "correct" : fields.String,
    "wrong" : fields.String,
    }

frq_fields = {
    "unique_id" : fields.String,
    "lecture_id" : fields.String,
    "question_num" : fields.Integer,
    "student_name" : fields.String,
    "session_id" : fields.String,
    "response" : fields.String
    }

class Question(Resource):
    @marshal_with(question_fields)
    def get(self, lectureId, questionNum):
        uniqueId = lectureId + "." + str(questionNum)
        to_get = QuizModel.query.filter_by(unique_id = uniqueId).first()
        if to_get is None:
            abort(404, message="That lecture id or question number does not exist")
        return to_get
    
    @marshal_with(question_fields)
    def post(self, lectureId, questionNum):
        args = questionPostArgs.parse_args()
        uniqueId = lectureId + "." + str(questionNum)
        result = QuizModel.query.filter_by(unique_id = uniqueId).first()
        if result is not None:
            abort(404, message="There is already a question with that number in this lecture")
        question = QuizModel(unique_id = uniqueId, lecture_id = lectureId, question_num = questionNum, question = args['question'], q_type = args["q_type"], correct = args['correct'], wrong = args['wrong'], session_id = args['session_id'])
        db.session.add(question)
        db.session.commit()
        return question, 201
    
    @marshal_with(question_fields)
    def delete(self, lectureId, questionNum):
        uniqueId = lectureId + "." + str(questionNum)
        to_delete = QuizModel.query.filter_by(unique_id = uniqueId).first()
        if to_delete is None:
            abort(404, message="That lecture id or question number does not exist")
        db.session.delete(to_delete)
        db.session.commit()
        return '', 204



class FRQ(Resource):
    @marshal_with(frq_fields)
    def get(self, lectureId, questionNum, studentName):
        uniqueId = lectureId + "." + str(questionNum) + "." + studentName
        get_response = FRQModel.query.filter_by(unique_id = uniqueId).first()
        if get_response is None:
            abort(404, message="There is no response by that student for that lecture question")
        return get_response

    @marshal_with(frq_fields)
    def post(self, lectureId, questionNum, studentName):
        args = FRQArgs.parse_args()
        uniqueId = lectureId + "." + str(questionNum) + "." + studentName
        post_response = FRQModel.query.filter_by(unique_id = uniqueId).first()
        if post_response is not None:
            abort(404, message="This student already responded to that question")
        response = FRQModel(unique_id = uniqueId, lecture_id = lectureId, question_num = questionNum, student_name = studentName, response = args['response'], session_id = args['session_id'])
        db.session.add(response)
        db.session.commit()
        return response, 201

    @marshal_with(frq_fields)
    def delete(self, lectureId, questionNum, studentName):
        uniqueId = lectureId + "." + str(questionNum) + "." + studentName
        delete_response = FRQModel.query.filter_by(unique_id = uniqueId).first()
        if delete_response is None:
            abort(404, message="There is no response by that student for that lecture question")
        db.session.delete(delete_response)
        db.session.commit()
        return '', 204

class Session(Resource):
    @marshal_with(question_fields)
    def get(self, sessionId):
        questions = QuizModel.query.filter_by(session_id = sessionId).all()
        return questions

class FRQSession(Resource):
    @marshal_with(frq_fields)
    def get(self, sessionId):
        responses = FRQModel.query.filter_by(session_id = sessionId).all()
        return responses

api.add_resource(Question, "/question/<string:lectureId>/<int:questionNum>")
api.add_resource(FRQ, "/frq/<string:lectureId>/<int:questionNum>/<string:studentName>")
api.add_resource(Session, "/question/<string:sessionId>")
api.add_resource(FRQSession, "/frq/<string:sessionId>")


if __name__ == "__main__":
    app.run(debug = True)

