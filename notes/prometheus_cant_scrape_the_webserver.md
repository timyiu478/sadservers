## "Warsaw": Prometheus can't scrape the webserver

### Problem

> A developer created a golang application that is exposing the /metrics endpoint. They have a problem with scraping the metrics from the application. They asked you to help find the problem. Full source code of the application is available at the /home/admin/app directory.

https://sadservers.com/scenario/warsaw

### Solution

1. try to curl the metrics HTTP endpoint

```
admin@i-003aa6b6ff49b7778:~$ curl -I -vvv http://localhost:9000/metrics 
*   Trying 127.0.0.1:9000...
* Connected to localhost (127.0.0.1) port 9000 (#0)
> HEAD /metrics HTTP/1.1
> Host: localhost:9000
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 405 Method Not Allowed
HTTP/1.1 405 Method Not Allowed
< Date: Tue, 01 Apr 2025 06:21:55 GMT
Date: Tue, 01 Apr 2025 06:21:55 GMT

< 
* Connection #0 to host localhost left intact
admin@i-003aa6b6ff49b7778:~$ curl -I -vvv http://localhost:9000/metrics -X POST
*   Trying 127.0.0.1:9000...
* Connected to localhost (127.0.0.1) port 9000 (#0)
> POST /metrics HTTP/1.1
> Host: localhost:9000
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
HTTP/1.1 200 OK
< Content-Type: text/plain; version=0.0.4; charset=utf-8; escaping=values
Content-Type: text/plain; version=0.0.4; charset=utf-8; escaping=values
< Date: Tue, 01 Apr 2025 06:22:13 GMT
Date: Tue, 01 Apr 2025 06:22:13 GMT
< Transfer-Encoding: chunked
Transfer-Encoding: chunked

< 
* Excess found: excess = 3939 url = /metrics (zero-length body)
* Connection #0 to host localhost left intact
```

2. try to find the processes that listen tcp connection with port 9000

```
admin@i-003aa6b6ff49b7778:~$ ps -aux | grep 9000
root         877  0.0  0.5 1671976 2444 ?        Sl   06:21   0:00 /usr/bin/docker-proxy -proto tcp -host-ip 0.0.0.0 -host-port 9000 -container-ip 172.18.0.2 -container-port 9000
root         884  0.0  0.5 1745452 2772 ?        Sl   06:21   0:00 /usr/bin/docker-proxy -proto tcp -host-ip :: -host-port 9000 -container-ip 172.18.0.2 -container-port 9000
admin       1471  0.0  0.1   5264   704 pts/0    S<+  06:30   0:00 grep 9000
admin@i-003aa6b6ff49b7778:~$ docker ps -l
CONTAINER ID   IMAGE             COMMAND                  CREATED         STATUS          PORTS                                       NAMES
63667d607fb1   prom/prometheus   "/bin/prometheus --c…"   13 months ago   Up 11 minutes   0.0.0.0:9090->9090/tcp, :::9090->9090/tcp   app-prometheus-1
```

3. check the process source code

It handles `/metrics` endpoint with `POST` method.

```
admin@i-003aa6b6ff49b7778:~/app$ cat main.go 
package main

import (
        "fmt"
        "log"
        "net/http"

        "github.com/gorilla/mux"
        "github.com/prometheus/client_golang/prometheus/promhttp"
)

func main() {
        router := mux.NewRouter()

        router.Handle("/metrics", promhttp.Handler()).Methods("POST")

        fmt.Println("Serving Prometheus metrics on http://localhost:9000/metrics")
        err := http.ListenAndServe(":9000", router)
        if err != nil {
                log.Fatal(err)
        }
}
```

4. update the method from `POST` to `GET`


```
        router.Handle("/metrics", promhttp.Handler()).Methods("GET")
```

5. build new golang image and run it

```
admin@i-003aa6b6ff49b7778:~/app$ docker compose up --build -d
[+] Building 0.7s (11/11) FINISHED                                                                                                                               docker:default
 => [golang-app internal] load build definition from Dockerfile.app                                                                                                        0.0s
 => => transferring dockerfile: 210B                                                                                                                                       0.0s
 => [golang-app internal] load metadata for docker.io/library/golang:1.20-alpine                                                                                           0.6s
 => [golang-app internal] load .dockerignore                                                                                                                               0.0s
 => => transferring context: 2B                                                                                                                                            0.0s
 => [golang-app 1/6] FROM docker.io/library/golang:1.20-alpine@sha256:e47f121850f4e276b2b210c56df3fda9191278dd84a3a442bfe0b09934462a8f                                     0.0s
 => => resolve docker.io/library/golang:1.20-alpine@sha256:e47f121850f4e276b2b210c56df3fda9191278dd84a3a442bfe0b09934462a8f                                                0.0s
 => [golang-app internal] load build context                                                                                                                               0.0s
 => => transferring context: 188B                                                                                                                                          0.0s
 => CACHED [golang-app 2/6] WORKDIR /app                                                                                                                                   0.0s
 => CACHED [golang-app 3/6] COPY go.mod go.sum ./                                                                                                                          0.0s
 => CACHED [golang-app 4/6] RUN go mod download                                                                                                                            0.0s
 => CACHED [golang-app 5/6] COPY . .                                                                                                                                       0.0s
 => CACHED [golang-app 6/6] RUN go build -o main .                                                                                                                         0.0s
 => [golang-app] exporting to image                                                                                                                                        0.0s
 => => exporting layers                                                                                                                                                    0.0s
 => => writing image sha256:f5a90710da27177958131d980566d08bbf67e72a6cf9d4b2a1a80be44582554d                                                                               0.0s
 => => naming to docker.io/library/app-golang-app                                                                                                                          0.0s
[+] Running 2/2
 ✔ Container golang-app        Started                                                                                                                                     1.3s 
 ✔ Container app-prometheus-1  Started                                                                                                                                     1.3s 
admin@i-003aa6b6ff49b7778:~/app$ docker ps -l
CONTAINER ID   IMAGE            COMMAND       CREATED          STATUS          PORTS                                       NAMES
fc6f06324cfc   app-golang-app   "/app/main"   20 seconds ago   Up 18 seconds   0.0.0.0:9000->9000/tcp, :::9000->9000/tcp   golang-app
```
