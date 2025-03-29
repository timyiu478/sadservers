## "Tokyo": can't serve web file

### Problem

> There's a web server serving a file /var/www/html/index.html with content "hello sadserver" but when we try to check it locally with an HTTP client like curl 127.0.0.1:80, nothing is returned. This scenario is not about the particular web server configuration and you only need to have general knowledge about how web servers work.

https://sadservers.com/scenario/tokyo

### Solution

1. the web server is `apache2` running on `tcp6 = TCP over IPv6` protocol.

Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      855/sshd: /usr/sbin 
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      440/systemd-resolve 
tcp6       0      0 :::80                   :::*                    LISTEN      611/apache2

2. check firewall rules

ufw:

```
root@i-08eeb3b772cf9210a:/etc/apache2# ufw status
Status: inactive
```

iptables:

```
Chain INPUT (policy ACCEPT 12662 packets, 111M bytes)
 pkts bytes target     prot opt in     out     source               destination         
   18  1080 DROP       tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpt:80
```

3. delete the iptable rule about dropping packets sent to prot 80

```
root@i-08eeb3b772cf9210a:/etc/apache2# iptables -D INPUT 1
root@i-08eeb3b772cf9210a:/etc/apache2# iptables -n -L -v
Chain INPUT (policy ACCEPT 12745 packets, 111M bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 10618 packets, 1209K bytes)
 pkts bytes target     prot opt in     out     source               destination
```

4. try `curl 127.0.0.1:80` and get 403 forbidden

```
root@i-00f5e2f57b0a66ff2:/# curl 127.0.0.1:80
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>403 Forbidden</title>
</head><body>
<h1>Forbidden</h1>
<p>You don't have permission to access this resource.</p>
<hr>
<address>Apache/2.4.52 (Ubuntu) Server at 127.0.0.1 Port 80</address>
</body></html>
root@i-00f5e2f57b0a66ff2:/#
```

5. check the `index.html` file access permission

```
root@i-00f5e2f57b0a66ff2:/etc/apache2# ls -alt /var/www/html
total 12
-rw------- 1 root root   16 Aug  1  2022 index.html
drwxr-xr-x 2 root root 4096 Aug  1  2022 .
drwxr-xr-x 3 root root 4096 Aug  1  2022 ..
```

6. allow web server to read the `index.html`

```
root@i-00f5e2f57b0a66ff2:/etc/apache2# chmod 444 /var/www/html/index.html 
root@i-00f5e2f57b0a66ff2:/etc/apache2# curl 127.0.0.1:80
```
