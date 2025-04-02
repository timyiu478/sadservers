## "Moyogalpa": Security Snag. The Trials of Mary and John

### Problem

> Mary and John are working on a Golang web application, and the security team has asked them to implement security measures. Unfortunately, they have broken the application, and it no longer functions. They need your help to fix it. The fixed application should be able to allow clients to communicate with the application over HTTPS without ignoring any checks. (eg: curl https://webapp:7000/users.html) and serve its static files.

https://sadservers.com/scenario/moyogalpa

### Solution

1. try to curl

* Could not resolve host: webapp

```
admin@i-01eae1763fec1ef11:~$ curl -vvv https://webapp:7000/users.html
* Could not resolve host: webapp
* Closing connection 0
curl: (6) Could not resolve host: webapp
```

2. find the `webapp`

- Its managed by systemd
- It cant open the ssl certificates

```
admin@i-01eae1763fec1ef11:~$ systemctl status webapp
● webapp.service - Webapp
     Loaded: loaded (/etc/systemd/system/webapp.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2025-04-02 11:11:54 UTC; 10min ago
   Main PID: 627 (webapp)
      Tasks: 4 (limit: 521)
     Memory: 4.6M
        CPU: 23ms
     CGroup: /system.slice/webapp.service
             └─627 /usr/local/bin/webapp

Apr 02 11:21:35 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:35 can not access certificate/key file. sleeping for 10s and will retry
Apr 02 11:21:45 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:45 open /home/webapp/pki/server.crt: permission denied
Apr 02 11:21:45 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:45 open /home/webapp/pki/server.pem: permission denied
Apr 02 11:21:45 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:45 can not access certificate/key file. sleeping for 10s and will retry
Apr 02 11:21:55 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:55 open /home/webapp/pki/server.crt: permission denied
Apr 02 11:21:55 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:55 open /home/webapp/pki/server.pem: permission denied
Apr 02 11:21:55 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:21:55 can not access certificate/key file. sleeping for 10s and will retry
Apr 02 11:22:05 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:22:05 open /home/webapp/pki/server.crt: permission denied
Apr 02 11:22:05 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:22:05 open /home/webapp/pki/server.pem: permission denied
Apr 02 11:22:05 i-01eae1763fec1ef11 webapp[627]: 2025/04/02 11:22:05 can not access certificate/key file. sleeping for 10s and will retry
admin@i-01eae1763fec1ef11:~$ systemctl cat webapp
# /etc/systemd/system/webapp.service
[Unit]
Description=Webapp
After=network.target

[Service]
Environment="APP_STATIC_DIR=/home/webapp/static-files" "APP_CERT=/home/webapp/pki/server.crt" "APP_KEY=/home/webapp/pki/server.pem"
Type=simple
User=webapp
Group=webapp
ExecStart=/usr/local/bin/webapp
TimeoutSec = 5
Restart = on-failure
RestartSec = 2

[Install]
WantedBy=multi-user.target
```

3. allow webapp to access the the ssl certificates and keys

```
admin@i-01eae1763fec1ef11:~$ ls -alt /home/webapp
total 28
drwx------ 2 root   root   4096 Apr 10  2024 pki
drwxr-xr-x 2 admin  admin  4096 Apr 10  2024 static-files
drwxr-xr-x 4 webapp webapp 4096 Apr 10  2024 .
drwxr-xr-x 4 root   root   4096 Apr 10  2024 ..
-rw-r--r-- 1 webapp webapp  220 Mar 27  2022 .bash_logout
-rw-r--r-- 1 webapp webapp 3526 Mar 27  2022 .bashrc
-rw-r--r-- 1 webapp webapp  807 Mar 27  2022 .profile
admin@i-01eae1763fec1ef11:~$ sudo chown webapp /home/webapp/pki
admin@i-01eae1763fec1ef11:~$ sudo chgrp webapp /home/webapp/pki
admin@i-01eae1763fec1ef11:~$ ls -alt /home/webapp
total 28
drwx------ 2 webapp webapp 4096 Apr 10  2024 pki
drwxr-xr-x 2 admin  admin  4096 Apr 10  2024 static-files
drwxr-xr-x 4 webapp webapp 4096 Apr 10  2024 .
drwxr-xr-x 4 root   root   4096 Apr 10  2024 ..
-rw-r--r-- 1 webapp webapp  220 Mar 27  2022 .bash_logout
-rw-r--r-- 1 webapp webapp 3526 Mar 27  2022 .bashrc
-rw-r--r-- 1 webapp webapp  807 Mar 27  2022 .profile
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chown webapp server.crt
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chown webapp server.pem
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chown webapp CA.crt 
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chgrp webapp server.crt
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chgrp webapp server.pen
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chgrp webapp server.pem
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo chgrp webapp CA.crt
admin@i-01eae1763fec1ef11:/home/webapp/pki$ ls -alt
total 20
drwxrwxrwx 2 webapp webapp 4096 Apr 10  2024 .
-rw-r----- 1 webapp webapp 1927 Apr 10  2024 server.crt
-rw-r----- 1 webapp webapp 3247 Apr 10  2024 server.pem
-rw-r----- 1 webapp webapp 1870 Apr 10  2024 CA.crt
drwxr-xr-x 4 webapp webapp 4096 Apr 10  2024 ..
```


4. restart web

```
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo systemctl restart webapp
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo systemctl status webapp
● webapp.service - Webapp
     Loaded: loaded (/etc/systemd/system/webapp.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2025-04-02 11:28:06 UTC; 6s ago
   Main PID: 1451 (webapp)
      Tasks: 4 (limit: 521)
     Memory: 1.0M
        CPU: 4ms
     CGroup: /system.slice/webapp.service
             └─1451 /usr/local/bin/webapp

Apr 02 11:28:06 i-01eae1763fec1ef11 systemd[1]: Stopping Webapp...
Apr 02 11:28:06 i-01eae1763fec1ef11 systemd[1]: webapp.service: Succeeded.
Apr 02 11:28:06 i-01eae1763fec1ef11 systemd[1]: Stopped Webapp.
Apr 02 11:28:06 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:28:06 Starting webserver, listening on port 7000
Apr 02 11:28:06 i-01eae1763fec1ef11 systemd[1]: Started Webapp.
```

5. try to curl

```
admin@i-01eae1763fec1ef11:/home/webapp/pki$ sudo netstat -tnpl 
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      652/sshd: /usr/sbin 
tcp6       0      0 :::34403                :::*                    LISTEN      1066/promtail       
tcp6       0      0 :::42959                :::*                    LISTEN      1066/promtail       
tcp6       0      0 :::6767                 :::*                    LISTEN      616/sadagent        
tcp6       0      0 :::8080                 :::*                    LISTEN      615/gotty           
tcp6       0      0 :::22                   :::*                    LISTEN      652/sshd: /usr/sbin 
tcp6       0      0 :::7000                 :::*                    LISTEN      1451/webapp         
admin@i-01eae1763fec1ef11:/home/webapp/pki$ curl https://webapp:7000/users.html
curl: (6) Could not resolve host: webapp
admin@i-01eae1763fec1ef11:/home/webapp/pki$ curl -vv https://webapp:7000/users.html
* Could not resolve host: webapp
* Closing connection 0
curl: (6) Could not resolve host: webapp
```

6. check local dns records

webapp is not found

```
admin@i-01eae1763fec1ef11:/home/webapp/pki$ cat /etc/hosts
# Your system has configured 'manage_etc_hosts' as True.
# As a result, if you wish for changes to this file to persist
# then you will need to either
# a.) make changes to the master file in /etc/cloud/templates/hosts.debian.tmpl
# b.) change or remove the value of 'manage_etc_hosts' in
#     /etc/cloud/cloud.cfg or cloud-config from user-data
#
127.0.1.1 i-01eae1763fec1ef11.us-east-2.compute.internal i-01eae1763fec1ef11
127.0.0.1 localhost

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
```

7. add `webapp` to resolve to ipv6 ip `::1`

```
# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback webapp
```

8. try to curl

SSL certificate problem: unable to get local issuer certificate

```
admin@i-01eae1763fec1ef11:/home/webapp/pki$ curl https://webapp:7000/users.html
curl: (60) SSL certificate problem: unable to get local issuer certificate
More details here: https://curl.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```

9. add the `webapp` certificate to local CA trust store

```
admin@i-01eae1763fec1ef11:/etc/ssl/certs$ sudo cp /home/webapp/pki/server.crt /usr/local/share/ca-certificates/
admin@i-01eae1763fec1ef11:/etc/ssl/certs$ sudo update-ca-certificates
Updating certificates in /etc/ssl/certs...
rehash: warning: skipping duplicate certificate in server.pem
1 added, 0 removed; done.
Running hooks in /etc/ca-certificates/update.d...
done.
```

10. try to curl

```
curl https://webapp:7000/users.html
Forbiddenadmin@i-01eae1763fec1ef11:~$ 
```

11. check the webapp logs

```
admin@i-01eae1763fec1ef11:~$ journalctl -u webapp -e
Apr 02 11:43:59 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:43:59 open /home/webapp/static-files/users.html: permission denied
Apr 02 11:44:38 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:44:38 open /home/webapp/static-files/users.html: permission denied
Apr 02 11:44:38 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:44:38 open /home/webapp/static-files/healthcheck.html: permission denied
Apr 02 11:44:50 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:44:50 open /home/webapp/static-files/users.html: permission denied
Apr 02 11:45:54 i-01eae1763fec1ef11 webapp[1451]: 2025/04/02 11:45:54 open /home/webapp/static-files/users.html: permission denied
```

12. allow `webapp` to access its static files


```
admin@i-01eae1763fec1ef11:/home/webapp$ sudo chown webapp static-files/
admin@i-01eae1763fec1ef11:/home/webapp$ sudo chgrp webapp static-files/
admin@i-01eae1763fec1ef11:/home/webapp$ cd static-files/
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ ls
file.html  healthcheck.html  users.html
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ sudo chown webapp *
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ sudo chgrp webapp *
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ ls -alt
total 20
drwxrwxrwx 2 webapp webapp 4096 Apr 10  2024 .
-rwxrwxrwx 1 webapp webapp   77 Apr 10  2024 file.html
-rwxrwxrwx 1 webapp webapp   78 Apr 10  2024 users.html
drwxr-xr-x 4 webapp webapp 4096 Apr 10  2024 ..
-rwxrwxrwx 1 webapp webapp   85 Apr 10  2024 healthcheck.html
```

13. try to curl 

```
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ curl https://webapp:7000/users.html
Forbiddenadmin@i-01eae1763fec1ef11:/home/webapp/static-files$ curl https://webapp:7000/file.html
Forbiddenadmin@i-01eae1763fec1ef11:/home/webapp/static-files$ curl https://webapp:7000/healthcheck.html
```

14. check the status of AppArmor

```
admin@i-01eae1763fec1ef11:/etc/apparmor.d$ sudo aa-status
apparmor module is loaded.
10 profiles are loaded.
10 profiles are in enforce mode.
   /usr/bin/man
   /usr/local/bin/webapp
   /usr/sbin/chronyd
   docker-default
   lsb_release
   man_filter
   man_groff
   nvidia_modprobe
   nvidia_modprobe//kmod
   tcpdump
0 profiles are in complain mode.
3 processes have profiles defined.
3 processes are in enforce mode.
   /usr/local/bin/webapp (2995) 
   /usr/sbin/chronyd (663) 
   /usr/sbin/chronyd (664) 
0 processes are in complain mode.
0 processes are unconfined but have a profile defined.
```

14. check AppArmor logs

```
admin@i-01eae1763fec1ef11:/home/webapp/static-files$ sudo dmesg | grep DENIED
[ 2342.651597] audit: type=1400 audit(1743594648.320:12): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/users.html" pid=1451 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1000
[ 2392.331963] audit: type=1400 audit(1743594697.999:13): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/users.html" pid=2841 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1000
[ 2443.612770] audit: type=1400 audit(1743594749.281:14): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/users.html" pid=2841 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1000
[ 2544.653392] audit: type=1400 audit(1743594850.313:15): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/users.html" pid=2841 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1001
[ 2565.649000] audit: type=1400 audit(1743594871.313:16): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/users.html" pid=2995 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1001
[ 2575.407036] audit: type=1400 audit(1743594881.068:17): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/file.html" pid=2995 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1001
[ 2583.016502] audit: type=1400 audit(1743594888.676:18): apparmor="DENIED" operation="open" profile="/usr/local/bin/webapp" name="/home/webapp/static-files/healthcheck.html" pid=2995 comm="webapp" requested_mask="r" denied_mask="r" fsuid=1001 ouid=1001
```

15. update apparmor config to allow webapp to open `/home/webapp/static-files/{users,healthcheck}.html`

```
admin@i-068d53ae8abb20961:/etc/apparmor.d$ cat usr.local.bin.webapp 
# Last Modified: Tue Mar 26 13:45:55 2024
include <tunables/global>

/usr/local/bin/webapp {
  include <abstractions/base>

  network inet stream,
  network inet6 stream,

  /proc/sys/net/core/somaxconn r,
  /sys/kernel/mm/transparent_hugepage/hpage_pmd_size r,
  /home/webapp/pki/ r,
  /home/webapp/pki/server.pem r,
  /home/webapp/pki/server.crt r,

  /home/webapp/static-files/ r,
  /home/webapp/static-files/users.html r,
  /home/webapp/static-files/healthcheck.html r,
}
admin@i-068d53ae8abb20961:/etc/apparmor.d$ sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.webapp
admin@i-068d53ae8abb20961:/etc/apparmor.d$ curl https://webapp:7000/users.html
<html>
  <head> </head>
  <body>
    <p>From Users Page</p>
  </body>
</html>
```

### Futher Study

1. https://apparmor.net/
