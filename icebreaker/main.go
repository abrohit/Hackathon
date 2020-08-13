package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/bmizerany/pat"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	// "github.com/julienschmidt/httprouter"
)

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

func (p *Person) String() {
	log.Printf("Person Name: %s/nPerson Match: %s", p.Username, p.Match)
}

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

//connect to mongodb, find people
func icebreaker(w http.ResponseWriter, r *http.Request) {
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
	filter := bson.D{{"match", "no"}}

	var result Person
	s := collection.FindOne(ctx, filter)
	//JSONData := &bson.D{}
	decodeError := s.Decode(&result)

	if decodeError != nil {
		log.Println("Decode error: ", decodeError)
	}

	fmt.Println("Path: ", result.Username)
	w.Write([]byte("Your partner is:"))
	w.Write([]byte(result.Username))

	// // if filtered == nil {
	// // 	w.Write([]byte("No partner available at this time"))
	// // 	w.Write([]byte("\n\n"))
	// // }
	// partner := filtered //[0]
	// fmt.Println(partner.username)

	//change to yes for partner and for user
	// _, err = collection.UpdateOne(
	// 	ctx,
	// 	partner,
	// 	bson.D{
	// 		{"$set", bson.D{{"match", "no"}}},
	// 	},
	// )
	//cookie and concurrency

	//when you exit icebreaker set everything to empty
	questions(w, r)
}

//one func to check connection
//one to find people
//one to match

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
