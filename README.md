<p align="center">
  <img src="/docs/public/hackthislogo.jpg" width="100px"></img>
  <img src="/docs/public/logoblack.png" width="100px"></img>

  <h3 align="center">
     Codebase for HackThis 2020 Submission: Classroom Plus
  </h3>
</p>

---
## ClientBot
A simple chatroom to pose questions and upvote, downvote, or comment 
on them.

### Running Locally
**ClientBot and Quiz**
```angular2
(venv) % python flask_start.py
```
The API is created at `http://localhost:9874`. 
Query with an app like [Insomnia](https://insomnia.rest/).

**Icebreaker**
```angular2
% cd icebreaker
% go run main.go
```

### Pushing to Heroku
**ClientBot and Quiz**
```angular2
% git commit
% git push heroku master
```

**Icebreaker**
```angular2
% cd icebreaker
% go mod vendor
% go build -i -o ./bin/icebreaker
% git commit
% git push heroku master
```

### API Endpoints
* All API Return `{ status: 1, response: ... }` or `{ status: 0, error: ... }`
* JWT Tokens are set to expire in 2 hours time

`POST /users/register`
* Request 

        {
            username: String,
            password: String,
            role: ["teacher"|"student"]
        }
* Returns
    * **Header**: `{ Authorization: "Bearer <JWT Token>" }`
    
`POST /users/authenticate`
* Request 

        {
            username: String,
            password: String
        }
* Returns
    * **Header**: `{ Authorization: "Bearer <JWT Token>" }`
    
`GET /users/current`
* Request 
    * Header: ` { Authorization } `
    
* Returns

        {
            id: String (user_id),
            username: String,
            role: ["teacher"|"student"]
        }

`GET /users/delete`
* Request 
    * Header: ` { Authorization } `
    
* Returns None

`GET /sessions`
* gets all online sessions
* Request None
* Returns

        {
            sessions: [
                {
                    session_id: int (session_id),
                    session_name: String,
                    opener: String (user_id),
                    lobby_size: int
                }
            ]
        }

`POST /sessions/new`
* creates a new session and names it `<username>'s Session` or, if passed a name in rbody, whatever that name is
* Request

        {
            session_name: String (optional)
        }

    * Header: ` { Authorization } `
* Returns

        {
            created: {
                session_id: int (session_id),
                session_name: String
            }
        }
        
`GET /sessions/enter`
* enters a session, placing the user in the session's lobby and **allowing them to run many of the below endpoints**
* Request

        {
            session_id: int (session_id)
        }

    * Header: ` { Authorization } `
* Returns None

`GET /sessions/leave`
* leaves a session, removing the user from the session's lobby and **denying them access to many of the below endpoints**
* Request

        {
            session_id: int (session_id)
        }
        
    * Header: ` { Authorization } `
* Returns None

`GET /sessions/delete`
* **only possible for session creator**
* Request
        {
            session_id: int (session_id)
        }
    * Header: ` { Authorization } `
* Returns None

`GET /sessions/get`
* a more in-depth look at a sessions, **requires user in session**
* Request

        {
            session_id: int (session_id)
        }
    * Header: ` { Authorization } `
* Returns

        {
            session_id: int (session_id),
            session_name: String,
            opener: String (user_id),
            doubts: [
                {
                    question: String,
                    comments: [
                        {
                            comment: String,
                            commenter: String (user_id),
                            comment_id: int (comment_id)
                        }
                    ],
                    poster: String (user_id),
                    doubt_id: int (doubt_id),
                    upvoters: [String (user_id)],
                    downvoters: [String (user_id)]
                }
            ],
            current_users: [String (user_id)]  // number of people in lobby
        }

`POST /doubt/new`
* posts a doubt, **requires user in session**
* Request

        {
            session_id: int (session_id),
            question: String
        }
    * Header: ` { Authorization } `
* Returns None

`GET /doubt/vote`
* votes on a doubt, **requires user in session**
* Request

        {
            session_id: int (session_id),
            doubt_id: int (doubt_id),
            type: ["upvote"|"downvote"|"neutral"]
        }
    * Header: ` { Authorization } `
* Returns something like "Upvoted", "Downvoted", "Neutralized", "Already upvoted, did nothing", etc...

`GET /doubt/resolve`
* resolves a doubt, **requires user in session AND doubt posted by user**
* Request

        {
            session_id: int (session_id),
            doubt_id: int (doubt_id)
        }
    * Header: ` { Authorization } `
* Returns None

`POST /doubt/comment`
* comments on a doubt, **requires user in session**
* Request

        {
            session_id: int (session_id),
            doubt_id: int (doubt_id),
            comment: String
        }
    * Header: ` { Authorization } `
* Returns None

`GET /doubt/comment/remove`
* removes comment on a doubt, **requires user in session AND comment posted by user or doubt posted by user**
* Request

        {
            session_id: int (session_id),
            doubt_id: int (doubt_id),
            comment_id: int (comment_id)
        }
    * Header: ` { Authorization } `
* Returns None

---
<h1 align="center">
     The Website!
  </h1>

## Function
It lets teachers and students have another platform to make classes more engaging and interactive. This is done through integrating a login/signup system and letting teachers create a session for students to join!

## Features
* It has a quiz function integrated that lets teachers create a quiz and students answer it. The quiz function also lets user have a free response category. This will allow the students to type the answers and let the teachers evaluate them at the end of the session! This was created to address the issue of classes not being engaging enough online.

* A Chatbox Feature also has been integrated in it! The chatbox lets users ask doubts/questions and lets other students answer them. The questions also has an upvote/downvote feature that lets teachers see which is the most asked doubt/question. This makes the class more interactive and provides another tool to help the teacher teach better!

* A notes feature! It lets students write notes and save them at the end of an session!

* On a side note, the website is also equipped with a signup system that verifies the user by email!

## Help

* The website is built in django. You can access it [here](https://github.com/abrohit/Hackathon/tree/master/ClassroomPlus2)

* The website will run when you run the manage.py using the command "python manage.py runserver" in the command prompt when you're in the directory of the file.

* The website will be functional at [localhost:8000](localhost:8000)

* If you need help starting it, visit [Django's official website!](https://www.djangoproject.com/start/)

## Authors
Fayed Raza, Rachael wei, Akaash Kolachina, Ricky Zhao, Nakul Iyer, Aryaman Singhal, and Rohit Manjunath
