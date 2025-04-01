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

10. change caddy to listen port 8088

it works.

```
admin@i-06d801d29173c69f1:/etc/caddy$ curl 127.0.0.1:8088
An error occurred: could not connect to server: Connection refused
        Is the server running on host "127.0.0.1" and accepting
        TCP/IP connections on port 5433?
```

11. check loaded kernel modules

the firewall rules related module e.g. `nft_chain_nat` is loaded

```
admin@i-0cecb9998cb582f0e:~$ lsmod
Module                  Size  Used by
nf_conntrack_netlink    57344  0
xfrm_user              45056  1
xfrm_algo              16384  1 xfrm_user
br_netfilter           32768  0
bridge                253952  1 br_netfilter
stp                    16384  1 bridge
llc                    16384  2 bridge,stp
dm_mod                163840  0
overlay               147456  0
nft_chain_nat          16384  4
xt_MASQUERADE          20480  1
nf_nat                 57344  2 nft_chain_nat,xt_MASQUERADE
xt_addrtype            16384  2
nft_counter            16384  16
xt_conntrack           16384  1
nf_conntrack          176128  4 xt_conntrack,nf_nat,nf_conntrack_netlink,xt_MASQUERADE
nf_defrag_ipv6         24576  1 nf_conntrack
nf_defrag_ipv4         16384  1 nf_conntrack
xt_tcpudp              20480  1
nft_compat             20480  5
nf_tables             274432  46 nft_compat,nft_counter,nft_chain_nat
libcrc32c              16384  3 nf_conntrack,nf_nat,nf_tables
nfnetlink              20480  4 nft_compat,nf_conntrack_netlink,nf_tables
nls_ascii              16384  1
nls_cp437              20480  1
vfat                   20480  1
fat                    86016  1 vfat
crct10dif_pclmul       16384  1
crc32_pclmul           16384  0
ghash_clmulni_intel    16384  0
aesni_intel           372736  0
crypto_simd            16384  1 aesni_intel
cryptd                 24576  2 crypto_simd,ghash_clmulni_intel
glue_helper            16384  1 aesni_intel
evdev                  24576  3
serio_raw              20480  0
button                 24576  0
fuse                  167936  1
configfs               57344  1
ip_tables              32768  0
x_tables               53248  6 xt_conntrack,nft_compat,xt_tcpudp,xt_addrtype,ip_tables,xt_MASQUERADE
autofs4                53248  2
ena                   118784  0
crc32c_intel           24576  3
```

12. check iptables

all packets to port 80 is dropped.

```
admin@i-0cecb9998cb582f0e:~$ sudo iptables -L -n

Chain INPUT (policy ACCEPT)
target     prot opt source               destination         
DROP       tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpt:80

Chain FORWARD (policy DROP)
target     prot opt source               destination         
DOCKER-USER  all  --  0.0.0.0/0            0.0.0.0/0           
DOCKER-ISOLATION-STAGE-1  all  --  0.0.0.0/0            0.0.0.0/0           
ACCEPT     all  --  0.0.0.0/0            0.0.0.0/0            ctstate RELATED,ESTABLISHED
DOCKER     all  --  0.0.0.0/0            0.0.0.0/0           
ACCEPT     all  --  0.0.0.0/0            0.0.0.0/0           
ACCEPT     all  --  0.0.0.0/0            0.0.0.0/0   
```

13. remove such iptables rule

```
admin@i-0cecb9998cb582f0e:~$ sudo iptables -D INPUT 1
```

14. try to curl 

Now, we can talk to the db_connector via caddy reverse proxy.
Lets fix the database now.

```
admin@i-0cecb9998cb582f0e:~$ curl localhost:80
An error occurred: could not connect to server: Connection refused
        Is the server running on host "127.0.0.1" and accepting
        TCP/IP connections on port 5433?
admin@i-0cecb9998cb582f0e:~$ curl localhost
An error occurred: could not connect to server: Connection refused
        Is the server running on host "127.0.0.1" and accepting
        TCP/IP connections on port 5433?
admin@i-0cecb9998cb582f0e:~$ curl 127.0.0.1
An error occurred: could not connect to server: Connection refused
        Is the server running on host "127.0.0.1" and accepting
        TCP/IP connections on port 5433?
```

15. check the status of postgresql

The postgresql unit is incorrect:

```
ExecStart=/bin/true
ExecReload=/bin/true
```

Details:

```
admin@i-0cecb9998cb582f0e:/var/log/postgresql$ cat postgresql-13-main.log 
2024-09-13 15:06:20.421 UTC [10687] LOG:  starting PostgreSQL 13.16 (Debian 13.16-0+deb11u1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
2024-09-13 15:06:20.421 UTC [10687] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2024-09-13 15:06:20.424 UTC [10687] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2024-09-13 15:06:20.430 UTC [10688] LOG:  database system was shut down at 2024-09-13 15:06:19 UTC
2024-09-13 15:06:20.436 UTC [10687] LOG:  database system is ready to accept connections
2024-09-13 15:07:18.874 UTC [10687] LOG:  received fast shutdown request
2024-09-13 15:07:18.877 UTC [10687] LOG:  aborting any active transactions
2024-09-13 15:07:18.882 UTC [10687] LOG:  background worker "logical replication launcher" (PID 10694) exited with exit code 1
2024-09-13 15:07:18.892 UTC [10689] LOG:  shutting down
2024-09-13 15:07:18.930 UTC [10687] LOG:  database system is shut down

admin@i-0cecb9998cb582f0e:/var/log/postgresql$ systemctl status postgresql.service 
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/lib/systemd/system/postgresql.service; disabled; vendor preset: enabled)
     Active: inactive (dead)

admin@i-0cecb9998cb582f0e:/var/log/postgresql$ systemctl cat postgresql
# /lib/systemd/system/postgresql.service
# systemd service for managing all PostgreSQL clusters on the system. This
# service is actually a systemd target, but we are using a service since
# targets cannot be reloaded.

[Unit]
Description=PostgreSQL RDBMS

[Service]
Type=oneshot
ExecStart=/bin/true
ExecReload=/bin/true
RemainAfterExit=on

[Install]
WantedBy=multi-user.target
```

```
admin@i-059cf7e283c5798aa:/var/lib/postgresql/13$ sudo -u postgres psql
```

```
postgres=# SELECT rolname, rolpassword FROM pg_authid;
          rolname          |             rolpassword             
---------------------------+-------------------------------------
 postgres                  | 
 pg_monitor                | 
 pg_read_all_settings      | 
 pg_read_all_stats         | 
 pg_stat_scan_tables       | 
 pg_read_server_files      | 
 pg_write_server_files     | 
 pg_execute_server_program | 
 pg_signal_backend         | 
 usuario                   | md51fb76ad714485db772076da0feb85d7f
```

dbname = os.getenv('DBNAME')
user = os.getenv('DBUSER')
password = os.getenv('DBPASSWORD')
host = os.getenv('DBHOST')
port = os.getenv('DBPORT')

### Lessons Learnt

1. check loaded kernel modules
1. `iptables` command is not found but we can `sudo iptables`
    1. `/sbin` is not in `$PATH` environment variable

```
admin@i-0cecb9998cb582f0e:~$ echo $PATH
/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games
admin@i-0cecb9998cb582f0e:~$ iptables
bash: iptables: command not found
admin@i-0cecb9998cb582f0e:~$ ls /sbin | grep iptables
iptables
iptables-apply
iptables-legacy
iptables-legacy-restore
iptables-legacy-save
iptables-nft
iptables-nft-restore
iptables-nft-save
iptables-restore
iptables-restore-translate
iptables-save
iptables-translate
```
