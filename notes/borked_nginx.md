## "Cape Town": Borked Nginx

### Problem

> There's an Nginx web server installed and managed by systemd. Running curl -I 127.0.0.1:80 returns curl: (7) Failed to connect to localhost port 80: Connection refused , fix it so when you curl you get the default Nginx page.

https://sadservers.com/scenario/capetown

### Solution

1. try to curl it first

```
admin@i-0d3b9b7a862020cf9:/$ curl -I 127.0.0.1:80
curl: (7) Failed to connect to 127.0.0.1 port 80: Connection refused
```

2. check active tcp connectoins 

port 80 connection is not found

```
admin@i-0d3b9b7a862020cf9:/$ netstat -nlp
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::6767                 :::*                    LISTEN      566/sadagent        
tcp6       0      0 :::8080                 :::*                    LISTEN      565/gotty           
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::38137                :::*                    LISTEN      -                   
tcp6       0      0 :::36747                :::*                    LISTEN      -                   
udp        0      0 127.0.0.1:323           0.0.0.0:*                           -                   
udp        0      0 0.0.0.0:68              0.0.0.0:*                           -                   
udp6       0      0 fe80::812:aeff:feb7:546 :::*                                -                   
udp6       0      0 ::1:323                 :::*  
```

3. check running process

No running process called nginx

```
admin@i-0d3b9b7a862020cf9:/$ ps -aux | grep nginx 
admin       1025  0.0  0.1   5204   648 pts/0    S<+  16:22   0:00 grep nginx
```

4. check nginx service status

```
admin@i-0d3b9b7a862020cf9:/$ systemctl status nginx
● nginx.service - The NGINX HTTP and reverse proxy server
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: failed (Result: exit-code) since Sat 2025-03-29 16:19:57 UTC; 4min 48s ago
        CPU: 25ms

Mar 29 16:19:57 i-0d3b9b7a862020cf9 systemd[1]: Starting The NGINX HTTP and reverse proxy server...
Mar 29 16:19:57 i-0d3b9b7a862020cf9 nginx[577]: nginx: [emerg] unexpected ";" in /etc/nginx/sites-enabled/default:1
Mar 29 16:19:57 i-0d3b9b7a862020cf9 nginx[577]: nginx: configuration file /etc/nginx/nginx.conf test failed
Mar 29 16:19:57 i-0d3b9b7a862020cf9 systemd[1]: nginx.service: Control process exited, code=exited, status=1/FAILURE
Mar 29 16:19:57 i-0d3b9b7a862020cf9 systemd[1]: nginx.service: Failed with result 'exit-code'.
Mar 29 16:19:57 i-0d3b9b7a862020cf9 systemd[1]: Failed to start The NGINX HTTP and reverse proxy server.
```

5. remove unexpected `;` in `/etc/nginx/sites-enabled/default` and then restart nginx

```
admin@i-0d3b9b7a862020cf9:/$ sudo systemctl restart nginx
admin@i-0d3b9b7a862020cf9:/$ systemctl status nginx
● nginx.service - The NGINX HTTP and reverse proxy server
     Loaded: loaded (/etc/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2025-03-29 16:27:53 UTC; 3s ago
    Process: 1154 ExecStartPre=/usr/sbin/nginx -t (code=exited, status=0/SUCCESS)
    Process: 1155 ExecStart=/usr/sbin/nginx (code=exited, status=0/SUCCESS)
   Main PID: 1157 (nginx)
      Tasks: 2 (limit: 524)
     Memory: 11.6M
        CPU: 36ms
     CGroup: /system.slice/nginx.service
             ├─1157 nginx: master process /usr/sbin/nginx
             └─1158 nginx: worker process

Mar 29 16:27:53 i-0d3b9b7a862020cf9 systemd[1]: Starting The NGINX HTTP and reverse proxy server...
Mar 29 16:27:53 i-0d3b9b7a862020cf9 nginx[1154]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
Mar 29 16:27:53 i-0d3b9b7a862020cf9 nginx[1154]: nginx: configuration file /etc/nginx/nginx.conf test is successful
Mar 29 16:27:53 i-0d3b9b7a862020cf9 systemd[1]: Started The NGINX HTTP and reverse proxy server.
```

6. try to curl

Got 500.

```
admin@i-0d3b9b7a862020cf9:/$ curl -I 127.0.0.1:80
HTTP/1.1 500 Internal Server Error
Server: nginx/1.18.0
Date: Sat, 29 Mar 2025 16:29:00 GMT
Content-Type: text/html
Content-Length: 177
Connection: close
```

7. check error log 

```
admin@i-0d3b9b7a862020cf9:/etc/nginx$ tail /var/log/nginx/error.log 
2025/03/29 16:42:45 [alert] 1695#1695: socketpair() failed (24: Too many open files)
2025/03/29 16:51:13 [alert] 1894#1894: socketpair() failed while spawning "worker process" (24: Too many open files)
2025/03/29 16:51:13 [emerg] 1895#1895: eventfd() failed (24: Too many open files)
2025/03/29 16:51:13 [alert] 1895#1895: socketpair() failed (24: Too many open files)
2025/03/29 16:51:16 [crit] 1895#1895: *1 open() "/var/www/html/index.nginx-debian.html" failed (24: Too many open files), client: 127.0.0.1, server: _, request: "HEAD / HTTP/1.1", host: "127.0.0.1"
```

8. check max open file limits of nginx

```
admin@i-041096f7b40e04ac0:/proc/1133$ cat limits | grep "open files"
Limit                     Soft Limit           Hard Limit           Units
Max open files            10                   10                   files
```

9. check max open file limits of OS

```
admin@i-041096f7b40e04ac0:/proc/1133$ ulimit -Hn
524288
```

10. increase max open file limits of nginx by updating nginx config

```
worker_rlimit_nofile 65535;
```
