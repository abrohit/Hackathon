SRCS := $(wildcard *.go)
GONAME=$(shell basename "$(PWD)")
PID=$(GONAME).pid

hello: 
	echo "Hello"

run: 
	go build -o $(GONAME) $(SRCS)
	echo "Starting $(GONAME)"
	./$(GONAME) & echo $$! > $(PID)

restart: 
	go run tcpC.go

stop:
	echo "Stopping ./$(GONAME) if it's running"
	-kill `[[ -f $(PID) ]] && cat $(PID)` 2>/dev/null || true

build:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o $(GONAME) $(SRCS)

beacon: build
	rsync -ae ssh $(GONAME) rachael@192.168.1.100:/home/rachael/golib

