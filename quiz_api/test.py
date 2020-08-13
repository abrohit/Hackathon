import requests


# THE ENDPOINTS:
# for get and post and delete methods for quiz questions, the endpoint is question/<string:lectureID>/<int:questionNUM>, with lecture id being
# the teacher's username + the lecture number. E.g a lecturer with the username Skola would have the following lectureId for their first lecture: Skola1.
# so to get or post the first question of Skola's 1st lecture, the endpoint would be question/Skola1/1.
# The endpoint for get and post and delete methods for FRQ responses is frq//<string:lectureID>/<int:questionNUM>/<string:studentName>, the lectureId works exactly like with quiz question
# requests, but there is now the addition of the student user whom the response belongs to. So to post the frq response by a student with username Bob to the second question
# asked in Skola's 1st lecture, the endpoint would be frq/Skola1/2/Bob.
# To get all the questions with a given session_id, the endpoint is question/<string:sessionId>, with the desired session_id.
# To get all the responses with a given session id the endpoint is frq/<string:sessionId>

BASE = "http://127.0.0.1:5000/"
to_post = {
           "question" : "What's 2+2?",
           'session_id' : "ABCD1234",
           "q_type" : "mc",
           "correct" : "4",
           "wrong" : "0  5  76"}
to_post_2 = { "question" : "What are the socioeconomic implications of airplane peanuts?",
              'session_id' : "ABCD1234",
              "q_type" : "frq",
              "correct" : "N/A",
              "wrong" : "N/A"}
to_post_3 = {"question" : "Inertia is a property of matter",
             'session_id' : "ABCD1234",
             "q_type" : "mc",
             "correct" : "True",
             "wrong" : "False"}
frq_post = {'session_id' : "ABCD1234",
            "response" :'''Airplane peanuts are actually one of the biggest players in the modern economy.
In this essay I will prove beyond a shadow of a doubt that income, class, and status are negligible. All that matters is airplane peanuts.'''}

frq_post_2 = {'session_id' : 'ABCD1234',
              'response' : '''Ross is the superior friend in "Friends" for a multitude of reasons. First of all, he likes dinosaurs, that's pretty cool.
Second of all...um...uhhh did I say the dinsaur thing already?'''}

if __name__ == "__main__"
    response = requests.post(BASE + "question/BNye89/99", to_post_3)
    print(response.json())
    input()
    response = requests.post(BASE + "question/BNye89/909", to_post_2)
    print(response.json())


    # posting = requests.post(BASE + "question/Skola1/1", question)
    to_get = requests.get(BASE + "question/Skola1/1")


    to_get = requests.get(BASE + "question/Skola1/2")
    print(to_get.json())

    frq_post = requests.get(BASE + "frq/Skola99/1/FakeStudent2")
    print(frq_post.json())
    questions = requests.get(BASE + "question/ABCD1234")
    print(questions.json())

    response = requests.post(BASE + "frq/Skola99/1/RossFan13", frq_post_2)
    print(response.json())
    response_2 = requests.post(BASE + "frq/FakeTeacher12/67/Student97", frq_post)
    input()
    responses = requests.get(BASE + "frq/ABCD1234")
    print(responses.json())
    check = requests.get(BASE + "question/BNye89/99")
    print(check.json())
    input()
    delete = requests.delete(BASE + "question/BNye89/99")
    check = requests.get(BASE + "question/BNye89/99")
    print(check.json())
    check = requests.get(BASE + "frq/Skola99/1/RossFan13")
    print(check.json())
    input()
    delete = requests.delete(BASE + "frq/Skola99/1/RossFan13")
    check = requests.get(BASE + "frq/Skola99/1/RossFan13")
    print(check.json())
