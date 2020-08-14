package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/julienschmidt/httprouter"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Store struct {
	mux sync.Mutex
}

type Questions struct {
	Index    string
	Question string
}

type Person struct {
	Id       primitive.ObjectID `bson:"_id" json: "_id"`
	Username string             `bson:"username" json: "username"`
	Password string             `bson:"password json: "password""`
	Role     string             `bson:"role" json: "role"`
	Match    string             `bson:"match" json: "match"`
	Email    string             `bson:"email" json: "email"`
	Phone    string             `bson:"phone" json: "phone"`
}

//Needed things:
//need distinct username, front-end to refresh the site
//Need to do:
//call a function when you exit a website

type rbody struct {
	User_name string
}

func determineListenAddress() string {
	port := os.Getenv("PORT")
	if port == "" {
		return ":3001"
	}
	return ":" + port
}

func main() {
	router := httprouter.New()
	router.GET("/questions", questions)
	router.GET("/icebreaker/:name/:password/:role/:email/:phone", icebreaker)
	log.Println("Listening...")
	err := http.ListenAndServe(":6002", router)
	if err != nil {
		log.Fatal(err)
	}
}

//{user_id, user_name, session_id}
//render(w, "icebreakersite.html", nil)
// email, ok := r.URL.Query()["email"]
// zoom, ok := r.URL.Query()["zoom"] // a boolean
// phone, ok := r.URL.Query()["phoneNumber"]
// if !ok || len(username[0]) < 1 || len(email[0]) < 1 || len(zoom[0]) < 1 || len(phone[0]) < 1 {
// 	log.Println("Url Param 'key' is missing")
// 	return
// }
func icebreaker(w http.ResponseWriter, r *http.Request, ps httprouter.Params) {

	//insert user in the database if new
	username := ps.ByName("name")
	password := ps.ByName("password")
	role := ps.ByName("role")
	email := ps.ByName("email")
	phone := ps.ByName("phone")
	user := insert(username, password, role, email, phone)
	c := Store{}
	partner := c.process(username)

	//write to port
	if partner != "" {
		u, _ := json.Marshal(user)
		w.Write([]byte(u))
	} else {
		w.Write([]byte("Refresh the website"))
	}
}

//goroutine to process through only two people at a time, set partners
func (c *Store) process(username string) string {
	var partner = ""
	c.mux.Lock()
	partner = c.connect(username)
	c.mux.Unlock()
	return partner
}

func (c *Store) connect(username string) string {
	ctx := context.Background()
	url := "mongodb+srv://dbUser:hackillinois2020@cluster0.8uvh8.mongodb.net/test?retryWrites=true&w=majority"
	clientOptions := options.Client().ApplyURI(url)
	client, err := mongo.NewClient(clientOptions)
	if err != nil {
		log.Fatal(err)
	}
	if err := client.Connect(ctx); err != nil {
		log.Fatal(err)
	}
	defer client.Disconnect(ctx)
	collection := client.Database("test").Collection("users")

	//find if there is match already
	var other []Person
	var us []Person
	partner := bson.D{{"match", username}}
	s, _ := collection.Find(ctx, partner)
	_ = s.All(ctx, &other)
	currentUser := bson.D{{"username", username}}
	currentData, _ := collection.Find(ctx, currentUser)
	_ = currentData.All(ctx, &us)
	//if we already have a match
	if us[0].Match != "" {
		return us[0].Match
	}
	//if there is not a match
	if other == nil {
		filter := bson.D{{"match", ""}}
		var partner []Person
		s, _ := collection.Find(ctx, filter)
		decodeError := s.All(ctx, &partner)
		if partner[0].Username == username {
			return ""
		}
		if decodeError != nil {
			log.Println("Decode error: ", decodeError)
		}
		//set current user data to other user's username
		_, err = collection.UpdateOne(
			ctx,
			bson.M{"username": username},
			bson.D{
				{"$set", bson.D{{"match", partner[0].Username}}},
			},
		)
		return partner[0].Username
		//if there is a match
	} else {
		_, err = collection.UpdateOne(
			ctx,
			bson.M{"username": username},
			bson.D{
				{"$set", bson.D{{"match", other[0].Username}}},
			},
		)
		return other[0].Username
	}
}

func insert(username string, password string, role string, email string, phone string) Person {
	ctx := context.Background()
	url := "mongodb+srv://dbUser:hackillinois2020@cluster0.8uvh8.mongodb.net/test?retryWrites=true&w=majority"
	clientOptions := options.Client().ApplyURI(url)
	client, err := mongo.NewClient(clientOptions)
	if err != nil {
		log.Fatal(err)
	}
	if err := client.Connect(ctx); err != nil {
		log.Fatal(err)
	}
	defer client.Disconnect(ctx)
	collection := client.Database("test").Collection("users")
	var user []Person
	s, _ := collection.Find(ctx, bson.D{{"username", username}})
	_ = s.All(ctx, &user)
	if user == nil {
		userData := Person{
			Id:       primitive.NewObjectID(),
			Username: username,
			Password: password,
			Role:     role,
			Match:    "",
			Email:    email,
			Phone:    phone,
		}
		_, insertErr := collection.InsertOne(ctx, userData)
		if insertErr != nil {
			fmt.Println("InsertOne ERROR:", insertErr)
			os.Exit(1) // safely exit script on error
		}
		return userData
	}
	return user[0]
}

//writes all questions
func questions(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
	w.Write([]byte("Questions:\n"))
	question1 := Questions{
		Index:    "1",
		Question: "What's your favorite color?",
	}
	question2 := Questions{
		Index:    "2",
		Question: "What's your favorite movie?",
	}
	question3 := Questions{
		Index:    "3",
		Question: "What came first: the chicken or the egg?",
	}
	question4 := Questions{
		Index:    "4",
		Question: "If you could travel anywhere would would you go?",
	}
	question5 := Questions{
		Index:    "5",
		Question: "What is a secret skill that you have?",
	}
	question6 := Questions{
		Index:    "6",
		Question: "If you had one day off, what would you do?",
	}

	q := []Questions{question1, question2, question3, question4, question5, question6}
	data, _ := json.Marshal(q)
	w.WriteHeader(200)
	w.Header().Set("Content-Type", "application/json")
	w.Write(data)
}

func render(w http.ResponseWriter, filename string, data interface{}) {
	tmpl, err := template.ParseFiles(filename)
	if err != nil {
		log.Println(err)
		http.Error(w, "Sorry, something went wrong", http.StatusInternalServerError)
	}

	if err := tmpl.Execute(w, data); err != nil {
		log.Println(err)
		http.Error(w, "Sorry, something went wrong", http.StatusInternalServerError)
	}
}
