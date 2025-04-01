## "Batumi": Troubleshoot "A" cannot connect to "B"

### Problem

https://sadservers.com/scenario/batumi

### Solution

1. try to curl

No http response back

```
admin@i-051ee5e3fff4646d7:~$ curl -vvv http://127.0.0.1
*   Trying 127.0.0.1:80...
```

2. check whether caddy is running

```
admin@i-051ee5e3fff4646d7:~$ ps -aux | grep caddy
caddy        609  0.0  5.6 1267244 26168 ?       Ssl  07:50   0:00 /usr/bin/caddy run --environ --config /etc/caddy/Caddyfile
```

3. check caddy config

```
admin@i-051ee5e3fff4646d7:~$ cat /etc/caddy/Caddyfile 
# The Caddyfile is an easy way to configure your Caddy web server.
#
# Unless the file starts with a global options block, the first
# uncommented line is always the address of your site.
#
# To use your own domain name (with automatic HTTPS), first make
# sure your domain's A/AAAA DNS records are properly pointed to
# this machine's public IP, then replace ":80" below with your
# domain name.

:80 {
        # Set this path to your site's directory.
# root * /usr/share/caddy

        # Enable the static file server.
    reverse_proxy localhost:5050

        # Another common task is to set up a reverse proxy:
        # reverse_proxy localhost:8080

        # Or serve a PHP site through php-fpm:
        # php_fastcgi localhost:9000
}

# Refer to the Caddy docs for more information:
# https://caddyserver.com/docs/caddyfile
```

4. curl client be able to connect with `localhost:5050`

```
admin@i-051ee5e3fff4646d7:~$ curl  -vv http://localhost:5050
*   Trying 127.0.0.1:5050...
* Connected to localhost (127.0.0.1) port 5050 (#0)
> GET / HTTP/1.1
> Host: localhost:5050
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 500 Internal Server Error
< Content-Length: 158
< 
An error occurred: could not connect to server: Connection refused
        Is the server running on host "127.0.0.1" and accepting
        TCP/IP connections on port 5433?
* Connection #0 to host localhost left intact
```

5. there is a `db_conector.py` running and here is its source code

Its binded `localhost:5050`

```
# script that retrieves secret from postgres database
import socket
import psycopg2
import logging
import sys
import os
from dotenv import load_dotenv, find_dotenv


# load secrets env var file .env
load_dotenv(find_dotenv())

# debugging
logging.basicConfig(level=logging.DEBUG,
                    handlers=[
                        logging.StreamHandler(sys.stdout),
                    ])

logging.debug("Starting db_connector...")


# Database connection parameters
dbname = os.getenv('DBNAME')
user = os.getenv('DBUSER')
password = os.getenv('DBPASSWORD')
host = os.getenv('DBHOST')
port = os.getenv('DBPORT')

db_params = {
    'dbname': dbname,
    'user': user,
    'password': password,
    'host': host,
    'port': port
}

# Create a socket and listen on port 5050
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5050))
server_socket.listen(1)

logging.debug("Listening on port 5050...")

while True:
    client_socket, addr = server_socket.accept()
    logging.debug(f"Connection from {addr}")

    try:
        # Read the HTTP request
        request = client_socket.recv(1024).decode()
        logging.debug(f"Received request: {request}")

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute("SELECT secret FROM secrets WHERE id=1;")
        result = cursor.fetchone()

        # Prepare the HTTP response
        if result:
            secret = result[0]
            response_body = secret.encode()
            response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_body)}\r\n\r\n".encode() + response_body
        else:
            response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 18\r\n\r\nNo secret found."

        # Send the HTTP response
        client_socket.sendall(response)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        logging.error(error_message)
        response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Length: {len(error_message)}\r\n\r\n{error_message}".encode()
        client_socket.sendall(response)

    finally:
        # Clean up
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        client_socket.close()
```

6. check the `DB*` environment variables

Its not found.

```
admin@i-051ee5e3fff4646d7:~$ printenv | grep DB
```

7. found caddy and db_connector are managed by systemd

Caddyfile is incorrect:

```
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"warn","ts":1743493812.2425418,"msg":"Caddyfile input is not formatted; run 'caddy fmt --overwrite' to fix inconsisten>
```

full:

```
admin@i-051ee5e3fff4646d7:~$ systemctl status caddy
● caddy.service - Caddy
     Loaded: loaded (/lib/systemd/system/caddy.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-04-01 07:50:12 UTC; 22min ago
       Docs: https://caddyserver.com/docs/
   Main PID: 609 (caddy)
      Tasks: 7 (limit: 521)
     Memory: 29.1M
        CPU: 229ms
     CGroup: /system.slice/caddy.service
             └─609 /usr/bin/caddy run --environ --config /etc/caddy/Caddyfile

Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"warn","ts":1743493812.2425418,"msg":"Caddyfile input is not formatted; run 'caddy fmt --overwrite' to fix inconsisten>
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2436557,"logger":"admin","msg":"admin endpoint started","address":"localhost:2019","enforce_ori>
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"warn","ts":1743493812.2448082,"logger":"http.auto_https","msg":"server is listening only on the HTTP port, so no auto>
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2461007,"logger":"tls.cache.maintenance","msg":"started background certificate maintenance","ca>
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2519455,"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2538862,"msg":"autosaved config (load with --resume flag)","file":"/var/lib/caddy/.config/caddy>
Apr 01 07:50:12 i-051ee5e3fff4646d7 systemd[1]: Started Caddy.
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.256642,"msg":"serving initial configuration"}
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2612562,"logger":"tls","msg":"cleaning storage unit","storage":"FileStorage:/var/lib/caddy/.loc>
Apr 01 07:50:12 i-051ee5e3fff4646d7 caddy[609]: {"level":"info","ts":1743493812.2616951,"logger":"tls","msg":"finished cleaning storage units"}
admin@i-051ee5e3fff4646d7:~$ systemctl status db_connector.service 
● db_connector.service - db_connector
     Loaded: loaded (/etc/systemd/system/db_connector.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-04-01 07:50:11 UTC; 22min ago
   Main PID: 614 (python3)
      Tasks: 1 (limit: 521)
     Memory: 9.5M
        CPU: 120ms
     CGroup: /system.slice/db_connector.service
             └─614 /usr/bin/python3 /home/admin/db_connector.py

Apr 01 07:56:42 i-051ee5e3fff4646d7 python3[614]:         TCP/IP connections on port 5433?
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: DEBUG:root:Connection from ('127.0.0.1', 47700)
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: DEBUG:root:Received request: GET / HTTP/1.1
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: Host: localhost:5050
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: User-Agent: curl/7.74.0
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: Accept: */*
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: 
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]: ERROR:root:An error occurred: could not connect to server: Connection refused
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]:         Is the server running on host "127.0.0.1" and accepting
Apr 01 07:56:48 i-051ee5e3fff4646d7 python3[614]:         TCP/IP connections on port 5433?
```

8. try to fix the Caddyfile

Caddy is listening tcp **v6** connection instead of the intended tcp **v4** connection.

```
admin@i-0aecd6ea251a98a33:/etc/caddy$ sudo netstat -tnlp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 127.0.0.1:2019          0.0.0.0:*               LISTEN      1591/caddy          
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      644/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:5050            0.0.0.0:*               LISTEN      623/python3         
tcp6       0      0 :::33323                :::*                    LISTEN      1062/promtail       
tcp6       0      0 :::6767                 :::*                    LISTEN      617/sadagent        
tcp6       0      0 :::8080                 :::*                    LISTEN      616/gotty           
tcp6       0      0 :::80                   :::*                    LISTEN      1591/caddy          
tcp6       0      0 :::22                   :::*                    LISTEN      644/sshd: /usr/sbin 
tcp6       0      0 :::39521                :::*                    LISTEN      1062/promtail       
admin@i-0aecd6ea251a98a33:/etc/caddy$ sudo systemctl status caddy
● caddy.service - Caddy
     Loaded: loaded (/lib/systemd/system/caddy.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2025-04-01 09:00:49 UTC; 3min 51s ago
       Docs: https://caddyserver.com/docs/
   Main PID: 1591 (caddy)
      Tasks: 7 (limit: 521)
     Memory: 11.5M
        CPU: 97ms
     CGroup: /system.slice/caddy.service
             └─1591 /usr/bin/caddy run --environ --config /etc/caddy/Caddyfile

Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.1983862,"msg":"adapted config to JSON","adapter":"caddyfile"}
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.1996074,"logger":"admin","msg":"admin endpoint started","address":"localhost:2019","enforce_or>
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"warn","ts":1743498049.1999204,"logger":"http.auto_https","msg":"server is listening only on the HTTP port, so no aut>
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.2001803,"logger":"tls.cache.maintenance","msg":"started background certificate maintenance","c>
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.200241,"logger":"http.log","msg":"server running","name":"srv0","protocols":["h1","h2","h3"]}
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.2005222,"msg":"autosaved config (load with --resume flag)","file":"/var/lib/caddy/.config/cadd>
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.2005844,"msg":"serving initial configuration"}
Apr 01 09:00:49 i-0aecd6ea251a98a33 systemd[1]: Started Caddy.
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.2082186,"logger":"tls","msg":"storage cleaning happened too recently; skipping for now","stora>
Apr 01 09:00:49 i-0aecd6ea251a98a33 caddy[1591]: {"level":"info","ts":1743498049.2083395,"logger":"tls","msg":"finished cleaning storage units"}
```

9. use this config for binding `127.0.0.1:80`

but `curl 127.0.0.1:80` still not works

```
admin@i-01b88a94bd2afc855:/etc/caddy$ cat Caddyfile 
# The Caddyfile is an easy way to configure your Caddy web server.
#
# Unless the file starts with a global options block, the first
# uncommented line is always the address of your site.
#
# To use your own domain name (with automatic HTTPS), first make
# sure your domain's A/AAAA DNS records are properly pointed to
# this machine's public IP, then replace ":80" below with your
# domain name.

:80 {
        # Set this path to your site's directory.
        # root * /usr/share/caddy

        # Enable the static file server.
        bind 127.0.0.1
        reverse_proxy localhost:5050

        # Another common task is to set up a reverse proxy:
        # reverse_proxy localhost:8080

        # Or serve a PHP site through php-fpm:
        # php_fastcgi localhost:9000
}

# Refer to the Caddy docs for more information:
# https://caddyserver.com/docs/caddyfile
admin@i-01b88a94bd2afc855:/etc/caddy$ sudo netstat -tnlp | grep caddy
tcp        0      0 127.0.0.1:2019          0.0.0.0:*               LISTEN      1191/caddy          
tcp        0      0 127.0.0.1:80            0.0.0.0:*               LISTEN      1191/caddy
```


