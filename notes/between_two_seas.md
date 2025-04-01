## "Tarifa": Between Two Seas

### Problem

> There are three Docker containers defined in the docker-compose.yml file: an HAProxy accepting connetions on port :5000 of the host, and two nginx containers, not exposed to the host. The person who tried to set this up wanted to have HAProxy in front of the (backend or upstream) nginx containers load-balancing them but something is not working.

https://sadservers.com/scenario/tarifa

### Solution

1. try to curl serveral times

It seems HAProxy always select nginx_0.

```
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$
```

2. check the `docker-compose.yml`

Something wrong about the network config:

- nginx_0, haproxy are on the frontend_network
- nginx_1 is on the backend_network

```
admin@i-03bc10a9caa90eb69:~$ cat docker-compose.yml 
version: '3'

services:
  nginx_0:
    image: nginx:1.25.3
    container_name: nginx_0
    restart: always
    volumes:
      - ./custom_index/nginx_0:/usr/share/nginx/html
      - ./custom-nginx_0.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend_network

  nginx_1:
    image: nginx:1.25.3
    container_name: nginx_1
    restart: always
    volumes:
      - ./custom_index/nginx_1:/usr/share/nginx/html
      - ./custom-nginx_1.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - backend_network

  haproxy:
    image: haproxy:2.8.4
    container_name: haproxy
    restart: always
    ports:
      - "5000:5000"
    depends_on:
      - nginx_0
      - nginx_1
    volumes:
      - ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro
    networks:
      - frontend_network

networks:
  frontend_network:
    driver: bridge
  backend_network:
    driver: bridge
```

3. check nginx, haproxy config

- haproxy config for nginx_1 is wrong.
- nginx_1 is listening port 81 instead of port 80

```
admin@i-03bc10a9caa90eb69:~$ cat custom-nginx_0.conf 
server {
    listen 80;

    server_name localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html;
    }
}admin@i-03bc10a9caa90eb69:~$ cat custom-nginx_1.conf 
server {
    listen 81;

    server_name localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html;
    }
}admin@i-03bc10a9caa90eb69:~$ cat haproxy.cfg 
global
    daemon
    maxconn 256

defaults
    mode http
    default-server init-addr last,libc,none
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http-in
    bind *:5000
    default_backend nginx_backends

backend nginx_backends
    balance roundrobin
    server nginx_0 nginx_0:80 check
    server nginx_1 nginx_1:80 check
```

4. update docker-compose.yaml and haproxy config based on the finding on (2) and (3)

docker-compose:

```
  nginx_1:
    image: nginx:1.25.3
    container_name: nginx_1
    restart: always
    volumes:
      - ./custom_index/nginx_1:/usr/share/nginx/html
      - ./custom-nginx_1.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - frontend_network
```

haproxy config:

```
backend nginx_backends
    balance roundrobin
    server nginx_0 nginx_0:80 check
    server nginx_1 nginx_1:81 check
```

5. run `docker compose start`

6. curl again

```
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_1
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_1
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_0
admin@i-03bc10a9caa90eb69:~$ curl localhost:5000
hello there from nginx_1
```
