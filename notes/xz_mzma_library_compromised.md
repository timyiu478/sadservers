## "Tukaani": XZ LZMA Library Compromised

### Problem

> The Linux shared library liblzma.so has been compromised (the real compromised XZ Utils liblzma has not been used). The liblzma.so at the path /usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5 is the good one. Consider the same library liblzma.so.5.2.5 at other paths as compromised or malicious (ideally we would have used other real versions with different checksums). Find all instances of this "malicious" liblzma library (remember, it's the same library but in different directory locations) and make it so none of the running processes use it, while the applications "webapp" and "jobapp" (both of which managed by systemd) still run properly (eg, stopping those applications is not a solution).

https://sadservers.com/scenario/tukaani

### Solution

1. check the path of the malicious shared library

It's `/opt/.trash/`.

```
admin@i-0fea63402637fbbd5:~$ lsof | grep liblzma.so.5
gotty      596                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  616 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  622 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  623 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  624 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  625 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1006 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1069 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1071 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  617 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  618 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  619 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  620 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
systemd    682                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
bash      1068                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
lsof      1141                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
grep      1142                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
lsof      1143                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
```

2. check the well-known environment variables or files for configuring the loaded shared library

```
admin@i-0fea63402637fbbd5:~$ echo $LD_PRELOAD

admin@i-0fea63402637fbbd5:~$ echo $LD_LIBRARY_PATH

admin@i-0fea63402637fbbd5:~$ cat /etc/ld.so.preload | grep '/opt/.trash'
/opt/.trash/liblzma.so.5
admin@i-0fea63402637fbbd5:~$ cat /etc/ld.so.cache | grep '/opt/.trash'
```

3. update `/etc/ld.so.preload` content to good library `/usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5`

```
admin@i-0fea63402637fbbd5:/etc$ sudo vim /etc/ld.so.preload
admin@i-0fea63402637fbbd5:/etc$ cat ld.so.preload 
/usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5
```

4. restart `webapp` and `jobapp` and check the list of open files 

```
admin@i-0fea63402637fbbd5:/etc$ sudo systemctl restart webapp
admin@i-0fea63402637fbbd5:/etc$ sudo systemctl restart jobapp
admin@i-0fea63402637fbbd5:/etc$ lsof | grep liblzma
gotty      596                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  616 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  622 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  623 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  624 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596  625 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1006 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1069 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
gotty      596 1071 gotty          admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  617 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  618 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  619 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
sadagent   597  620 sadagent       admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
systemd    682                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
bash      1068                     admin  mem       REG              259,1   158400     265777 /opt/.trash/liblzma.so.5
lsof      1480                     admin  mem       REG              259,1   158400       1509 /usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5
grep      1481                     admin  mem       REG              259,1   158400       1509 /usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5
lsof      1482                     admin  mem       REG              259,1   158400       1509 /usr/lib/x86_64-linux-gnu/liblzma.so.5.2.5
```

5. check the unit file of `webapp`

We can see `environment="LD_LIBRARY_PATH=/opt/.trash/"` and we should remove it (we have the `ld.so.preload` for loading the good one already).

```
admin@i-038c3f542784effb0:~$ systemctl cat webapp
# /etc/systemd/system/webapp.service
[Unit]
Description=Webapp
After=network.target

[Service]
ExecStart = /opt/webapp/webapp.py
User = root
Group = root
Type = simple
TimeoutSec = 5
Environment="LD_LIBRARY_PATH=/opt/.trash/"
Restart = on-failure
RestartSec = 2

[Install]
WantedBy=multi-user.target
```

6. remove `environment="LD_LIBRARY_PATH=/opt/.trash/"` in `/etc/systemd/system/webapp.service` and restart the `webapp`

```
admin@i-038c3f542784effb0:~$ sudo vim /etc/systemd/system/webapp.service
admin@i-038c3f542784effb0:~$ sudo systemctl daemon-reload
admin@i-038c3f542784effb0:~$ sudo systemctl restart webapp
admin@i-038c3f542784effb0:~$ sudo systemctl status webapp
● webapp.service - Webapp
     Loaded: loaded (/etc/systemd/system/webapp.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2025-04-03 08:14:25 UTC; 8s ago
   Main PID: 1345 (python3)
      Tasks: 1 (limit: 521)
     Memory: 8.3M
        CPU: 61ms
     CGroup: /system.slice/webapp.service
             └─1345 python3 /opt/webapp/webapp.py

Apr 03 08:14:25 i-038c3f542784effb0 systemd[1]: Stopping Webapp...
Apr 03 08:14:25 i-038c3f542784effb0 systemd[1]: webapp.service: Succeeded.
Apr 03 08:14:25 i-038c3f542784effb0 systemd[1]: Stopped Webapp.
Apr 03 08:14:25 i-038c3f542784effb0 systemd[1]: Started Webapp.
```

7. check the unit file of `jobapp`


The file hints us to check `/opt/.trash/.jobapp.env`


```
admin@i-038c3f542784effb0:~$ sudo systemctl cat jobapp
# /etc/systemd/system/jobapp.service
[Unit]
Description=jobapp
After=network.target

[Service]
ExecStart = /opt/job-app/jobapp.py
User = root
Group = root
Type = simple
TimeoutSec = 5
EnvironmentFile=/opt/.trash/.jobapp.env
Restart = on-failure
RestartSec = 2

[Install]
WantedBy=multi-user.target
```

8. check `/opt/.trash/.jobapp.env`

```
admin@i-038c3f542784effb0:~$ cat /opt/.trash/.jobapp.env
APP_CONFIG_DB_NAME="jobapp"
APP_CONFIG_USER="dev"
LD_PRELOAD="/opt/.trash/liblzma.so.5"
DB_CONFIG_PRELOAD="true"
```

9. remove `LD_PRELOAD="/opt/.trash/liblzma.so.5"` in `/opt/.trash/.jobapp.env` and restart `jobapp`

```
admin@i-038c3f542784effb0:~$ sudo vim /opt/.trash/.jobapp.env 
admin@i-038c3f542784effb0:~$ sudo systemctl restart jobapp
admin@i-038c3f542784effb0:~$ sudo systemctl status jobapp
● jobapp.service - jobapp
     Loaded: loaded (/etc/systemd/system/jobapp.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2025-04-03 08:19:30 UTC; 5s ago
   Main PID: 1415 (python3)
      Tasks: 1 (limit: 521)
     Memory: 2.5M
        CPU: 15ms
     CGroup: /system.slice/jobapp.service
             └─1415 python3 /opt/job-app/jobapp.py

Apr 03 08:19:30 i-038c3f542784effb0 systemd[1]: jobapp.service: Succeeded.
Apr 03 08:19:30 i-038c3f542784effb0 systemd[1]: Stopped jobapp.
Apr 03 08:19:30 i-038c3f542784effb0 systemd[1]: Started jobapp.
```

10. reboot the server to reflect the changes to all processes

```
sudo reboot
```
