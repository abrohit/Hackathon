package main

import (
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"sync"

	"github.com/bmizerany/pat"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Store struct {
	num int
	p1  string
	p2  string
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
}

//call a function when you exit a website

func main() {
	mux := pat.New()
	mux.Get("/questions", http.HandlerFunc(questions))
	mux.Get("/icebreaker", http.HandlerFunc(icebreaker))
	log.Println("Listening...")
	err := http.ListenAndServe(":3000", mux)
	if err != nil {
		log.Fatal(err)
	}
}

//put the person's username in this from frontend
func getUserID() string {
	return "testing"
}

//{user_id, user_name, session_id}
//take if they want email, ft or zoom, phone number
func icebreaker(w http.ResponseWriter, r *http.Request) {
	//render(w, "icebreakersite.html", nil)
	keys, ok := r.URL.Query()["user_name"]

	if !ok || len(keys[0]) < 1 {
		log.Println("Url Param 'key' is missing")
		return
	}
	currentUsername := keys[0]
	c := Store{num: 0}
	partner := c.process(currentUsername)
	if partner != "" {
		w.Write([]byte(partner))
	}
}

//goroutine to process through only two people at a time, set partners
func (c *Store) process(username string) string {
	var partner = ""
	if c.num == 2 {
		fmt.Println("equal to two")
		c.mux.Lock()
		partner = c.connect(username, true)
		c.p1 = ""
		c.p2 = ""
		c.mux.Unlock()
	}
	if c.num < 2 {
		fmt.Println("less than 2")
		c.mux.Lock()
		result := c.connect(username, false)
		if result == "" {
			if c.p1 == "" {
				c.p1 = username
			} else {
				c.p2 = username
			}
		}
		c.mux.Unlock()
		fmt.Println("p1 and p2", c.p1, c.p2)
	}
	return partner
}

func (c *Store) connect(username string, toSwitch bool) string {
	fmt.Println("connect")
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
	//if not to Switch
	if !toSwitch {
		filter := bson.D{{"username", username}}
		var result Person
		s := collection.FindOne(ctx, filter)
		decodeError := s.Decode(&result)

		if decodeError != nil {
			log.Println("Decode error: ", decodeError)
		}
		return result.Match
	} else {
		//don't know if this is necessary
		f1 := bson.D{{"username", c.p1}}
		f2 := bson.D{{"username", c.p2}}
		var p1 Person
		var p2 Person
		s := collection.FindOne(ctx, f1)
		s2 := collection.FindOne(ctx, f2)
		_, err = collection.UpdateOne(
			ctx,
			s.Decode(&p1),
			bson.D{
				{"$set", bson.D{{"match", p2}}},
			},
		)
		_, err = collection.UpdateOne(
			ctx,
			s2.Decode(&p2),
			bson.D{
				{"$set", bson.D{{"match", p1}}},
			},
		)
		if c.p1 == username {
			return c.p2
		} else {
			return c.p1
		}
	}
}

//writes all questions
func questions(w http.ResponseWriter, r *http.Request) {
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
