## "Melbourne": WSGI with Gunicorn

### Problem

> There is a Python WSGI web application file at /home/admin/wsgi.py , the purpose of which is to serve the string "Hello, world!". This file is served by a Gunicorn server which is fronted by an nginx server (both servers managed by systemd). So the flow of an HTTP request is: Web Client (curl) -> Nginx -> Gunicorn -> wsgi.py . The objective is to be able to curl the localhost (on default port :80) and get back "Hello, world!", using the current setup.

https://sadservers.com/scenario/melbourne

### Solution

1. try to curl and see the error response

```
admin@i-0b8f3c1ef41e0a7b7:/$ curl -vvv http://localhost
*   Trying 127.0.0.1:80...
* connect to 127.0.0.1 port 80 failed: Connection refused
* Failed to connect to localhost port 80: Connection refused
* Closing connection 0
curl: (7) Failed to connect to localhost port 80: Connection refused
```

2. check the status of nginx

its inactive.

```
admin@i-0b8f3c1ef41e0a7b7:~$ systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; disabled; vendor preset: enabl>
     Active: inactive (dead)
       Docs: man:nginx(8)
```


3. try to restart nginx

Its active now.

```
admin@i-0b8f3c1ef41e0a7b7:~$ sudo systemctl restart nginx
admin@i-0b8f3c1ef41e0a7b7:~$ systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; disabled; vendor preset: enabl>
     Active: active (running) since Mon 2025-03-31 07:48:02 UTC; 44s ago
       Docs: man:nginx(8)
    Process: 1163 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; >
    Process: 1165 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exi>
   Main PID: 1166 (nginx)
      Tasks: 3 (limit: 524)
     Memory: 12.0M
        CPU: 46ms
     CGroup: /system.slice/nginx.service
             ├─1166 nginx: master process /usr/sbin/nginx -g daemon on; master_process>
             ├─1167 nginx: worker process
             └─1168 nginx: worker process

Mar 31 07:48:02 i-0b8f3c1ef41e0a7b7 systemd[1]: Starting A high performance web server>
Mar 31 07:48:02 i-0b8f3c1ef41e0a7b7 systemd[1]: Started A high performance web server
```

4. check the status of Gunicorn

Its also active.

```
dmin@i-0b8f3c1ef41e0a7b7:~$ systemctl status gunicorn
● gunicorn.service - gunicorn daemon
     Loaded: loaded (/etc/systemd/system/gunicorn.service; enabled; vendor preset: ena>
     Active: active (running) since Mon 2025-03-31 07:38:42 UTC; 10min ago
TriggeredBy: ● gunicorn.socket
   Main PID: 592 (gunicorn)
      Tasks: 2 (limit: 524)
     Memory: 17.3M
        CPU: 351ms
     CGroup: /system.slice/gunicorn.service
             ├─592 /usr/bin/python3 /usr/local/bin/gunicorn --bind unix:/run/gunicorn.>
             └─661 /usr/bin/python3 /usr/local/bin/gunicorn --bind unix:/run/gunicorn.>

Mar 31 07:38:42 i-0b8f3c1ef41e0a7b7 systemd[1]: Started gunicorn daemon.
Mar 31 07:38:43 i-0b8f3c1ef41e0a7b7 gunicorn[592]: [2025-03-31 07:38:43 +0000] [592] [>
Mar 31 07:38:43 i-0b8f3c1ef41e0a7b7 gunicorn[592]: [2025-03-31 07:38:43 +0000] [592] [>
Mar 31 07:38:43 i-0b8f3c1ef41e0a7b7 gunicorn[592]: [2025-03-31 07:38:43 +0000] [592] 
```

5. try to curl

Nginx response 502 Bad Gateway.

```
admin@i-0b8f3c1ef41e0a7b7:~$ curl localhost
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.18.0</center>
</body>
</html>
```

6. check the log of nginx

```
admin@i-0b8f3c1ef41e0a7b7:/var/log/nginx$ cat error.log
2025/03/31 07:50:22 [crit] 1167#1167: *1 connect() to unix:/run/gunicorn.socket failed (2: No such file or directory) while connecting to upstream, client: 127.0.0.1, server: , request: "GET / HTTP/1.1", upstream: "http://unix:/run/gunicorn.socket:/", host: "localhost"
```

7. check `gunicorn.socket`

Its `gunicorn.sock` instead of `gunicorn.socket`

```
admin@i-0b8f3c1ef41e0a7b7:/var/log/nginx$ ls /run/gunicorn.sock -alt
srw-rw-rw- 1 root root 0 Mar 31 07:38 /run/gunicorn.sock
```

8. update nginx config and restart it

```
admin@i-0d90eed88f6a08d27:/etc/nginx/sites-available$ cat default
server {
    listen 80;

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

9. try to curl

Content-Length: 0

```
admin@i-0d90eed88f6a08d27:/etc/nginx/sites-available$ curl -v localhost
*   Trying 127.0.0.1:80...
* Connected to localhost (127.0.0.1) port 80 (#0)
> GET / HTTP/1.1
> Host: localhost
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Server: nginx/1.18.0
< Date: Mon, 31 Mar 2025 08:32:52 GMT
< Content-Type: text/html
< Content-Length: 0
< Connection: keep-alive
< 
* Connection #0 to host localhost left intact
```

10. check `wsgi.py`

```
admin@i-0b8f3c1ef41e0a7b7:~$ cat wsgi.py 
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', '0'), ])
    return [b'Hello, world!']
```

11. change `Content-Lenght` to `13` and restart gunicorn

```
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html'), ('Content-Length', '13'), ])
    return [b'Hello, world!']
```
