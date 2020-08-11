package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/bmizerany/pat"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
	"go.mongodb.org/mongo-driver/mongo/readpref"
	// "github.com/julienschmidt/httprouter"
)

type Questions struct {
	Index    string
	Question string
}

// type person struct {
// 	ID       string
// 	Name     string
// 	Password string
// 	Role     string
// }
type person struct {
	ID          primitive.ObjectID `bson:"_id,omitempty"`
	Podcast     primitive.ObjectID `bson:"podcast,omitempty"`
	Title       string             `bson:"title,omitempty"`
	Description string             `bson:"description,omitempty"`
	Duration    int32              `bson:"duration,omitempty"`
}

func main() {
	mux := pat.New()
	mux.Get("/questions", http.HandlerFunc(questions))
	mux.Get("/icebreaker", http.HandlerFunc(icebreaker))
	log.Println("Listening...")
	err := http.ListenAndServe(":1002", mux)
	if err != nil {
		log.Fatal(err)
	}
}

//enter icebreaker
func icebreaker(w http.ResponseWriter, r *http.Request) {
	url := "mongodb+srv://dbUser:hackillinois2020@cluster0.8uvh8.mongodb.net/test?retryWrites=true&w=majority"
	clientOptions := options.Client().ApplyURI(url)
	client, err := mongo.NewClient(clientOptions)
	if err != nil {
		log.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	err = client.Connect(ctx)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Disconnect(ctx)
	err = client.Ping(ctx, readpref.Primary())
	if err != nil {
		log.Fatal(err)
	}
	collection := client.Database("test").Collection("users")
	cursor, err := collection.Find(ctx, bson.M{})
	if err != nil {
		log.Fatal(err)
	}
	var people []bson.M
	if err = cursor.All(ctx, &people); err != nil {
		log.Fatal(err)
	}
	fmt.Println(people)
	//filter through to get those with string "no"
	fmt.Println("\n\n")
	filterCursor, err := collection.Find(ctx, bson.M{"match": "no"})
	if err != nil {
		log.Fatal(err)
	}
	var peopleFiltered []bson.M
	if err = filterCursor.All(ctx, &peopleFiltered); err != nil {
		log.Fatal(err)
	}
	if peopleFiltered != nil {
		w.Write([]byte("No partner available at this time"))
		w.Write([]byte("\n\n"))
	}
	partner := peopleFiltered[0]
	//write username of matched partner
	// w.Write([]byte(partner))
	//change to yes for partner and for user
	_, err = collection.UpdateOne(
		ctx,
		partner,
		bson.D{
			{"$set", bson.D{{"match", "yes"}}},
		},
	)
	//when you exit icebreaker set everything to no
	questions(w, r)
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
