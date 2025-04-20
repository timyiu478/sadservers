## "Florence": Database Migration Hell

### Problem

You are working as a DevOps Engineer in a company and another team member left the company and left the docker-compose.yml of a database-backed web application unfinished.

Generally, the problem revolves around the database migration and docker compose.

Additionally on front of the application there is an Nginx server and you need to fix the proper access to it as well.

The source of code is in `/home/admin/app`

https://sadservers.com/scenario/florence

### Solution

1. try `curl --cacert /etc/nginx/certs/sadserver.crt https://sadserver.local`

```
admin@i-0c18b2e98cab87ded:~$ curl --cacert /etc/nginx/certs/sadserver.crt https://sadserver.local
curl: (6) Could not resolve host: sadserver.local
```

2. check the status of the `nginx`

what is `ssl_stapling`?


```
admin@i-0c18b2e98cab87ded:~$ systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Sun 2025-04-20 07:42:12 UTC; 3min 5s ago
       Docs: man:nginx(8)
   Main PID: 633 (nginx)
      Tasks: 3 (limit: 521)
     Memory: 8.3M
        CPU: 59ms
     CGroup: /system.slice/nginx.service
             ├─633 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─634 nginx: worker process
             └─635 nginx: worker process

Apr 20 07:42:12 i-0c18b2e98cab87ded nginx[602]: nginx: [warn] "ssl_stapling" ignored, issuer certificate not found for certificate "/etc/nginx/certs/>
Apr 20 07:42:11 i-0c18b2e98cab87ded systemd[1]: Starting A high performance web server and a reverse proxy server...
Apr 20 07:42:12 i-0c18b2e98cab87ded nginx[625]: nginx: [warn] "ssl_stapling" ignored, issuer certificate not found for certificate "/etc/nginx/certs/>
Apr 20 07:42:12 i-0c18b2e98cab87ded systemd[1]: nginx.service: Failed to parse PID from file /run/nginx.pid: Invalid argument
Apr 20 07:42:12 i-0c18b2e98cab87ded systemd[1]: Started A high performance web server and a reverse proxy server.
```

3. check the config of nginx

the `server_name` is correct

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ cat default 
server {
    listen 80;
    server_name sadserver.local;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name sadserver.local;
    include ssl/ssl_params.conf;

    ssl_certificate /etc/nginx/certs/sadserver.crt;
    ssl_certificate_key /etc/nginx/certs/sadserver.key;

    location / {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_pass http://localhost:9000/;
        proxy_ssl_session_reuse off;
        proxy_set_header Host $http_host;
        proxy_pass_header Server;
        proxy_cache_bypass $http_upgrade;
        proxy_redirect off;
    }
```

4. teach local DNS how resolve `sadserver.local`

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ cat /etc/hosts | grep sad
127.0.0.1 localhost sadserver.local
```

5. try to curl again

curl: (60) SSL certificate problem: certificate has expired

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ curl --cacert /etc/nginx/certs/sadserver.crt https://sadserver.local
curl: (60) SSL certificate problem: certificate has expired
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```

6. check datetime from OS point of view

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ date
Sun Apr 20 07:56:55 UTC 2025
```

7. check the SSL cert expiration time

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ openssl x509 -in /etc/nginx/certs/sadserver.crt -text -noout
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            2b:87:59:6e:f6:81:1f:e9:7e:02:c1:5f:78:e8:a7:6c:6f:b1:fb:d0
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = sadserver.local
        Validity
            Not Before: Mar 10 12:38:24 2024 GMT
            Not After : Mar 11 12:38:24 2024 GMT
```

8. check whether I have the right to renew the cert

```
admin@i-0c18b2e98cab87ded:/etc/nginx/certs$ ls -alt
total 16
drwxr-xr-x 10 root  root  4096 Apr 15  2024 ..
drwxr-xr-x  2 admin admin 4096 Apr 15  2024 .
-rw-r--r--  1 admin admin 1704 Apr 15  2024 sadserver.key
-rw-r--r--  1 admin admin 1318 Apr 15  2024 sadserver.crt
```

9. renew SSL cert

```
admin@i-0c18b2e98cab87ded:/etc/nginx/certs$ openssl req -new -key sadserver.key -out new_request.csr
admin@i-0c18b2e98cab87ded:/etc/nginx/certs$ openssl x509 -req -days 365 -in new_request.csr -signkey sadserver.key -out sadserver.crt
Signature ok
subject=C = AU, ST = Some-State, O = Internet Widgits Pty Ltd, CN = sadserver.local
Getting Private key
admin@i-0c18b2e98cab87ded:/etc/nginx/certs$ openssl x509 -in sadserver.crt -noout -enddate
notAfter=Apr 20 08:05:22 2026 GMT
admin@i-08580a039972ad8ea:/etc/nginx/certs$ sudo systemctl restart nginx
```


10. try to curl again

502: indicate server side problem

```
admin@i-0c18b2e98cab87ded:/usr/local/share/ca-certificates$ sudo systemctl restart nginx
admin@i-0c18b2e98cab87ded:/usr/local/share/ca-certificates$ curl --cacert /etc/nginx/certs/sadserver.crt https://sadserver.local
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.18.0</center>
</body>
</html>
```

11. check any process listen to `localhost:9000`

Nope.

```
admin@i-0c18b2e98cab87ded:/etc/nginx/sites-available$ sudo netstat -tclpn 
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:443             0.0.0.0:*               LISTEN      2543/nginx: master  
tcp        0      0 0.0.0.0:5000            0.0.0.0:*               LISTEN      858/docker-proxy    
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      2543/nginx: master  
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      616/sshd: /usr/sbin 
tcp6       0      0 :::35229                :::*                    LISTEN      1132/promtail       
tcp6       0      0 :::5000                 :::*                    LISTEN      864/docker-proxy    
tcp6       0      0 :::6767                 :::*                    LISTEN      589/sadagent        
tcp6       0      0 :::8080                 :::*                    LISTEN      588/gotty           
tcp6       0      0 :::39477                :::*                    LISTEN      1132/promtail       
tcp6       0      0 :::22                   :::*                    LISTEN      616/sshd: /usr/sbin 
```

12. check the docker running containers and `docker-compose.yml`

- only local docker registry is up.
- the system is a layered architecture: REST API -> Database
- no shared network
- the `DATABASE_URL` of `api` service is weird

```
admin@i-0c18b2e98cab87ded:~/app$ cat docker-compose.yml 
version: '3.8'

services:
  db:
    container_name: db
    build: postgresql
    restart: always
    ports:
      - 5432:5432
    environment:
      POSTGRES_PASSWORD: postgres
  api:
    container_name: api
    build: api
    ports:
      - 9000:9000
    environment:
      - PORT=9000
      - DATABASE_URL=db
  api_aggregator:
    container_name: api_aggregator
    build: api_aggregator
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      DATABASE_URL: postgres://api_aggregator:sadserver@db:5432/postgres

admin@i-0c18b2e98cab87ded:~/app$ docker ps
CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS          PORTS                                       NAMES
4536ab037265   registry:2   "/entrypoint.sh /etc…"   12 months ago   Up 31 minutes   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   docker-registry
```

13. try to run `docker compose up`

```
api             | 2025/04/20 08:21:01 server has started
api             | 2025/04/20 08:21:01 error starting the database dial tcp 172.18.0.2:5432: connect: connection refused
db              | initdb: cannot be run as root
db              | Please log in (using, e.g., "su") as the (unprivileged) user that will
db              | own the server process.
db exited with code 1
```

14. fix the `docker-compose.yml`

- added share bridge network
- let `db` runs as `postgres` user
- let `api` wait for `db` become ready
- let `api_aggregator` wait for `api` become ready

```
version: '3.8'

services:
  db:
    container_name: db
    build: postgresql
    restart: always
    ports:
      - 5432:5432
    environment:
      POSTGRES_PASSWORD: postgres
    user: "postgres:postgres"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - shared_network
  api:
    container_name: api
    build: api
    ports:
      - 9000:9000
    environment:
      - PORT=9000
      - DATABASE_URL=db
    depends_on:
      db:
        condition: service_healthy
    networks:
      - shared_network
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://api:9000"]
      interval: 10s
      timeout: 5s
      retries: 5
  api_aggregator:
    container_name: api_aggregator
    build: api_aggregator
    ports:
      - "3000:3000"
    depends_on:
      api:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://api_aggregator:md53ag67f31cc3e581ceas40fe1f36541e54@db:5432/postgres
    networks:
      - shared_network

networks:
  shared_network:
    driver: bridge
```

15. try `docker compose up`

```
db              | FATAL:  no pg_hba.conf entry for host "172.18.0.4", user "api_aggregator", database "postgres", SSL off
api_aggregator  | /usr/src/app/node_modules/pg-protocol/dist/parser.js:287
api_aggregator  |         const message = name === 'notice' ? new messages_1.NoticeMessage(length, messageValue) : new messages_1.DatabaseError(messageValue, length, name);
api_aggregator  |                                                                                                  ^
api_aggregator  | 
api_aggregator  | error: no pg_hba.conf entry for host "172.18.0.4", user "api_aggregator", database "postgres", SSL off
api_aggregator  |     at Parser.parseErrorMessage (/usr/src/app/node_modules/pg-protocol/dist/parser.js:287:98)
api_aggregator  |     at Parser.handlePacket (/usr/src/app/node_modules/pg-protocol/dist/parser.js:126:29)
api_aggregator  |     at Parser.parse (/usr/src/app/node_modules/pg-protocol/dist/parser.js:39:38)
api_aggregator  |     at Socket.<anonymous> (/usr/src/app/node_modules/pg-protocol/dist/index.js:11:42)
api_aggregator  |     at Socket.emit (node:events:513:28)
api_aggregator  |     at addChunk (node:internal/streams/readable:324:12)
api_aggregator  |     at readableAddChunk (node:internal/streams/readable:297:9)
api_aggregator  |     at Readable.push (node:internal/streams/readable:234:10)
api_aggregator  |     at TCP.onStreamRead (node:internal/stream_base_commons:190:23) {
api_aggregator  |   length: 158,
api_aggregator  |   severity: 'FATAL',
api_aggregator  |   code: '28000',
api_aggregator  |   detail: undefined,
api_aggregator  |   hint: undefined,
api_aggregator  |   position: undefined,
api_aggregator  |   internalPosition: undefined,
api_aggregator  |   internalQuery: undefined,
api_aggregator  |   where: undefined,
api_aggregator  |   schema: undefined,
api_aggregator  |   table: undefined,
api_aggregator  |   column: undefined,
api_aggregator  |   dataType: undefined,
api_aggregator  |   constraint: undefined,
api_aggregator  |   file: 'auth.c',
api_aggregator  |   line: '490',
api_aggregator  |   routine: 'ClientAuthentication'
api_aggregator  | }
api_aggregator  | 
api_aggregator  | Node.js v18.14.1
```

16. add `pg_hba.conf` to allow user login

remember to delete the image to force the docker compose rebuild the image

```
up and runningadmin@i-0669ed54dc37b476f:~/app/postgresql$ cat entrypoint.sh 
#!/bin/sh
set -e

echo "Need some time before running the database..."
sleep 5
if [ ! -f /var/lib/postgresql/data/initialized ]; then
    initdb -D /var/lib/postgresql/data
    touch /var/lib/postgresql/data/initialized

fi

echo "host all  postgres   0.0.0.0/0  trust" >> /var/lib/postgresql/data/pg_hba.conf
echo "host all  sadserver   0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf
echo "host all  api_aggregator   0.0.0.0/0  md5" >> /var/lib/postgresql/data/pg_hba.conf


exec postgres
```
