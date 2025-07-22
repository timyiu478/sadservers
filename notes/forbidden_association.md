##  "Fukuoka": Forbidden Association

### Problem

Description: There's a web server running on this host but curl localhost returns the default 404 Not Found page.

Fix the issue so that a file is served correctly and the message Welcome to the Real Site! is returned.

ref: https://sadservers.com/scenario/fukuoka

### Solution

1. check which process is listening port 80 or is web sever

nginx.

```
admin@i-05f23ad9320dab719:~$ sudo netstat -tupln
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      627/nginx: master p 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      611/sshd: /usr/sbin 
tcp6       0      0 :::41701                :::*                    LISTEN      718/promtail        
tcp6       0      0 :::6767                 :::*                    LISTEN      582/sadagent        
tcp6       0      0 :::80                   :::*                    LISTEN      627/nginx: master p 
tcp6       0      0 :::8080                 :::*                    LISTEN      581/gotty           
tcp6       0      0 :::46355                :::*                    LISTEN      718/promtail        
tcp6       0      0 :::22                   :::*                    LISTEN      611/sshd: /usr/sbin 
udp        0      0 127.0.0.1:323           0.0.0.0:*                           609/chronyd         
udp        0      0 0.0.0.0:68              0.0.0.0:*                           389/dhclient        
udp6       0      0 fe80::96:a2ff:fe55::546 :::*                                487/dhclient        
udp6       0      0 ::1:323                 :::*                                609/chronyd
```

2. update nginx config

```
admin@i-05f23ad9320dab719:/etc/nginx/sites-enabled$ cat default | grep Welcome -B 5 -A 5
        # location / { # First attempt to serve request as file, then # as directory, then fall back to displaying a 404.  try_files $uri $uri/ =404; }
        #
        location / {
                default_type text/html;
                add_header Content-Type "text/html; charset=utf-8";
                return 200 '<html><body>Welcome to the Real Site!</body></html>';
        }
```

3. restart nginx

```

```
