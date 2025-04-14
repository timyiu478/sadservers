## "Pokhara": SSH and other sshenanigans

### Problem

A user client was added to the server, as well as their SSH public key.

The objective is to be able to SSH locally (there's only one server) as this user client using their ssh keys. This is, if as root you change to this user sudo su; su client, you should be able to login with ssh: ssh localhost.

https://sadservers.com/scenario/pokhara

### Solution

1. try `sudo -u client ssh client@localhost 'pwd'`

```
admin@i-019a4b9bc446dddb4:/$ sudo -u client ssh client@localhost 'pwd'
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!
It is also possible that a host key has just been changed.
The fingerprint for the ECDSA key sent by the remote host is
SHA256:YYDr9SiTS21hSgZ2LlfjiXkwnFmCcohiOeC52J6Kokc.
Please contact your system administrator.
Add correct host key in /home/client/.ssh/known_hosts to get rid of this message.
Offending ECDSA key in /home/client/.ssh/known_hosts:1
  remove with:
  ssh-keygen -f "/home/client/.ssh/known_hosts" -R "localhost"
ECDSA host key for localhost has changed and you have requested strict checking.
Host key verification failed.
```

2. switch to client user

```
admin@i-019a4b9bc446dddb4:~/.ssh$ sudo -u client bash
client@i-019a4b9bc446dddb4:~/.ssh$ whoami
client
```

3. gather SSH public keys from localhost ssh server and add those keys to `known_hosts`

```
client@i-019a4b9bc446dddb4:~/.ssh$ ssh-keyscan localhost >> ~/.ssh/known_hosts
# localhost:22 SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
# localhost:22 SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
# localhost:22 SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
# localhost:22 SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
# localhost:22 SSH-2.0-OpenSSH_8.4p1 Debian-5+deb11u1
```

4. try `sudo -u client ssh client@localhost 'pwd'`

```
admin@i-019a4b9bc446dddb4:~/.ssh$ sudo -u client ssh client@localhost 'pwd'
client@localhost: Permission denied (publickey).
```

5. get some info about the SSH server

```
dmin@i-019a4b9bc446dddb4:~/.ssh$ sudo netstat -tcnlp | grep 22
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      619/sshd: /usr/sbin 
tcp6       0      0 :::22                   :::*                    LISTEN      619/sshd: /usr/sbin 
^C
admin@i-019a4b9bc446dddb4:~/.ssh$ systemd status sshd
Excess arguments.
admin@i-019a4b9bc446dddb4:~/.ssh$ systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-07 06:09:24 UTC; 18min ago
       Docs: man:sshd(8)
             man:sshd_config(5)
   Main PID: 619 (sshd)
      Tasks: 1 (limit: 524)
     Memory: 4.9M
        CPU: 519ms
     CGroup: /system.slice/ssh.service
             └─619 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups

Apr 07 06:23:40 i-019a4b9bc446dddb4 sshd[1173]: Connection closed by 127.0.0.1 port 40838 [preauth]
Apr 07 06:23:40 i-019a4b9bc446dddb4 sshd[1174]: Connection closed by 127.0.0.1 port 40840 [preauth]
Apr 07 06:23:40 i-019a4b9bc446dddb4 sshd[1175]: Unable to negotiate with 127.0.0.1 port 40842: no matching host key type found. Their offer: sk-ecdsa-sha2-nistp256@openssh.com>
Apr 07 06:23:40 i-019a4b9bc446dddb4 sshd[1176]: Unable to negotiate with 127.0.0.1 port 40844: no matching host key type found. Their offer: sk-ssh-ed25519@openssh.com [preaut>
Apr 07 06:24:23 i-019a4b9bc446dddb4 sshd[1187]: User client from 127.0.0.1 not allowed because listed in DenyUsers
Apr 07 06:24:23 i-019a4b9bc446dddb4 sshd[1187]: Connection closed by invalid user client 127.0.0.1 port 40846 [preauth]
Apr 07 06:24:52 i-019a4b9bc446dddb4 sshd[1196]: User client from 127.0.0.1 not allowed because listed in DenyUsers
Apr 07 06:24:52 i-019a4b9bc446dddb4 sshd[1196]: Connection closed by invalid user client 127.0.0.1 port 40850 [preauth]
Apr 07 06:25:48 i-019a4b9bc446dddb4 sshd[1339]: User client from 127.0.0.1 not allowed because listed in DenyUsers
Apr 07 06:25:48 i-019a4b9bc446dddb4 sshd[1339]: Connection closed by invalid user client 127.0.0.1 port 40856 [preauth]
admin@i-019a4b9bc446dddb4:~/.ssh$ systemctl cat sshd
# /lib/systemd/system/ssh.service
[Unit]
Description=OpenBSD Secure Shell server
Documentation=man:sshd(8) man:sshd_config(5)
After=network.target auditd.service
ConditionPathExists=!/etc/ssh/sshd_not_to_be_run

[Service]
EnvironmentFile=-/etc/default/ssh
ExecStartPre=/usr/sbin/sshd -t
ExecStart=/usr/sbin/sshd -D $SSHD_OPTS
ExecReload=/usr/sbin/sshd -t
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure
RestartPreventExitStatus=255
Type=notify
RuntimeDirectory=sshd
RuntimeDirectoryMode=0755

[Install]
WantedBy=multi-user.target
Alias=sshd.service
```

6. Enable public key authentication by uncomment `PubkeyAuthentication` and `AuthorizedKeysFile`

```
admin@i-019a4b9bc446dddb4:/etc/ssh$ cat sshd_config | grep Au
# Authentication:
#MaxAuthTries 6
#PubkeyAuthentication yes
#AuthorizedKeysFile     .ssh/authorized_keys .ssh/authorized_keys2
#AuthorizedPrincipalsFile none
admin@i-019a4b9bc446dddb4:/etc/ssh$ sudo systemctl restart sshd
```

7. add client public key to SSH server's authorized_keys

```
root@i-019a4b9bc446dddb4:/home/client/.ssh# cat id_rsa.pub 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDQopf1DsoscAMwsWJL1V1F1GHom1+qwkp0QlXnfWP+bKwkXZfTj+IIvtEZ3ECyIQa2bMEFdME9aU67vJoF4X3KSvQQijxr9ng5fWhVxvCauYdVi4UU1NtvHtw7RUj+gIIwcqmOg2/wwhRb7zjN53arsaJu0P77VOhwTRYI0fcUX6iE+W6wNvKRBvnZShSla5pCk0x7Ox2wptYfTnbIOx6+me7g9fkctakm1yeujsRbQjJHwkfdLfYhMJkT4wibLvJSooB5WIe62ioCcFbiHEywMrrdKH8oCy8i8wD28S5vh6FTZiZxBX6nL7HModXQI9RV6mZ9TE/ZovWYCk3Cp0675JoWEM94C53S+5eVtZTj4l2ZsYwmc8WaJiullLYdWEYi2jtmnHxsnFQ/YZ/Tf9zndRBVUPKuG84mGzJ5Fs28w0u5SiNeHdS0OOHvAcGnuoweKigt01JRJdt8DZO+N8jCEM/jo1TST131sy1TLyylY6zBe6ID/uoyWkVLc5/iFhM= client@somehost
admin@i-019a4b9bc446dddb4:~/.ssh$ cat authorized_keys | grep client
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDQopf1DsoscAMwsWJL1V1F1GHom1+qwkp0QlXnfWP+bKwkXZfTj+IIvtEZ3ECyIQa2bMEFdME9aU67vJoF4X3KSvQQijxr9ng5fWhVxvCauYdVi4UU1NtvHtw7RUj+gIIwcqmOg2/wwhRb7zjN53arsaJu0P77VOhwTRYI0fcUX6iE+W6wNvKRBvnZShSla5pCk0x7Ox2wptYfTnbIOx6+me7g9fkctakm1yeujsRbQjJHwkfdLfYhMJkT4wibLvJSooB5WIe62ioCcFbiHEywMrrdKH8oCy8i8wD28S5vh6FTZiZxBX6nL7HModXQI9RV6mZ9TE/ZovWYCk3Cp0675JoWEM94C53S+5eVtZTj4l2ZsYwmc8WaJiullLYdWEYi2jtmnHxsnFQ/YZ/Tf9zndRBVUPKuG84mGzJ5Fs28w0u5SiNeHdS0OOHvAcGnuoweKigt01JRJdt8DZO+N8jCEM/jo1TST131sy1TLyylY6zBe6ID/uoyWkVLc5/iFhM= client@somehost
admin@i-019a4b9bc446dddb4:~/.ssh$ sudo systemctl restart sshd
```

8. try `sudo -u client ssh client@localhost 'pwd'`

```
admin@i-019a4b9bc446dddb4:~/.ssh$ sudo -u client ssh client@localhost 'pwd'
client@localhost: Permission denied (publickey).
```

9. check the SSH server logs

User client from 127.0.0.1 not allowed because listed in DenyUsers.

```
admin@i-019a4b9bc446dddb4:/etc/ssh$ systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-07 06:44:13 UTC; 3min 26s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 1675 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
   Main PID: 1676 (sshd)
      Tasks: 1 (limit: 524)
     Memory: 1.1M
        CPU: 42ms
     CGroup: /system.slice/ssh.service
             └─1676 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups

Apr 07 06:44:13 i-019a4b9bc446dddb4 systemd[1]: Starting OpenBSD Secure Shell server...
Apr 07 06:44:13 i-019a4b9bc446dddb4 sshd[1676]: Server listening on 0.0.0.0 port 22.
Apr 07 06:44:13 i-019a4b9bc446dddb4 sshd[1676]: Server listening on :: port 22.
Apr 07 06:44:13 i-019a4b9bc446dddb4 systemd[1]: Started OpenBSD Secure Shell server.
Apr 07 06:44:15 i-019a4b9bc446dddb4 sshd[1683]: User client from 127.0.0.1 not allowed because listed in DenyUsers
Apr 07 06:44:15 i-019a4b9bc446dddb4 sshd[1683]: Connection closed by invalid user client 127.0.0.1 port 40902 [preauth]
```

10. found `DenyUsers client`

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ cat sad.conf 
DenyUsers client
```

11. remove `sad.conf`

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo rm sad.conf 
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo systemctl restart sshd
```

12. try `sudo -u client ssh client@localhost 'pwd'`

Permissions 0644 for '/home/client/.ssh/id_rsa' are too open.

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo -u client ssh client@localhost 'pwd'
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/client/.ssh/id_rsa' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/client/.ssh/id_rsa": bad permissions
client@localhost: Permission denied (publickey).
```

13. update `id_rsa` permissions 

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo -u client chmod 0600 /home/client/.ssh/id_rsa
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo -u client ls -alt /home/client/.ssh/id_rsa
-rw-r----- 1 client client 2610 Feb  5  2023 /home/client/.ssh/id_rsa
```

14. try `sudo -u client ssh client@localhost 'pwd'`

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo -u client ssh client@localhost 'pwd'
Your account has expired; please contact your system administrator.
Connection closed by 127.0.0.1 port 22
```

15. check the logs of SSH server

Apr 07 06:52:51 i-019a4b9bc446dddb4 sshd[1840]: pam_unix(sshd:account): account client has expired (account expired)
Apr 07 06:52:51 i-019a4b9bc446dddb4 sshd[1840]: fatal: Access denied for user client by PAM account configuration [preauth]

```
admin@i-019a4b9bc446dddb4:/etc/ssh/sshd_config.d$ sudo systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-07 06:49:10 UTC; 4min 42s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 1785 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
   Main PID: 1786 (sshd)
      Tasks: 1 (limit: 524)
     Memory: 1.1M
        CPU: 87ms
     CGroup: /system.slice/ssh.service
             └─1786 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups

Apr 07 06:49:10 i-019a4b9bc446dddb4 systemd[1]: Starting OpenBSD Secure Shell server...
Apr 07 06:49:10 i-019a4b9bc446dddb4 sshd[1786]: Server listening on 0.0.0.0 port 22.
Apr 07 06:49:10 i-019a4b9bc446dddb4 sshd[1786]: Server listening on :: port 22.
Apr 07 06:49:10 i-019a4b9bc446dddb4 systemd[1]: Started OpenBSD Secure Shell server.
Apr 07 06:49:18 i-019a4b9bc446dddb4 sshd[1798]: Connection closed by authenticating user client 127.0.0.1 port 40916 [preauth]
Apr 07 06:52:34 i-019a4b9bc446dddb4 sshd[1824]: Connection closed by authenticating user client 127.0.0.1 port 40928 [preauth]
Apr 07 06:52:51 i-019a4b9bc446dddb4 sshd[1840]: pam_unix(sshd:account): account client has expired (account expired)
Apr 07 06:52:51 i-019a4b9bc446dddb4 sshd[1840]: fatal: Access denied for user client by PAM account configuration [preauth]
```

16. find what SSH configs about `PAM`

./sshd_config:UsePAM yes

```
admin@i-019a4b9bc446dddb4:/etc/ssh$ grep -r 'PAM' .
./sshd_config:# some PAM modules and threads)
./sshd_config:# Set this to 'yes' to enable PAM authentication, account processing,
./sshd_config:# and session processing. If this is enabled, PAM authentication will
./sshd_config:# PasswordAuthentication.  Depending on your PAM configuration,
./sshd_config:# PAM authentication via ChallengeResponseAuthentication may bypass
./sshd_config:# If you just want the PAM account and session checks to run without
./sshd_config:# PAM authentication, then enable this but set PasswordAuthentication
./sshd_config:UsePAM yes
```

17. turn off PAM authentication

```
admin@i-019a4b9bc446dddb4:/etc/ssh$ sudo vim sshd_config
admin@i-019a4b9bc446dddb4:/etc/ssh$ cat sshd_config | grep UsePAM
UsePAM no
admin@i-019a4b9bc446dddb4:/etc/ssh$ sudo systemctl restart sshd
```

18. try `sudo -u client ssh client@localhost 'pwd'`

Account client has expired.

```
admin@i-019a4b9bc446dddb4:/etc/ssh$ sudo -u client ssh client@localhost 'pwd'
client@localhost: Permission denied (publickey).
admin@i-019a4b9bc446dddb4:/etc/ssh$ sudo systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-07 06:59:05 UTC; 31s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 1907 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
   Main PID: 1908 (sshd)
      Tasks: 1 (limit: 524)
     Memory: 1.0M
        CPU: 43ms
     CGroup: /system.slice/ssh.service
             └─1908 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups

Apr 07 06:59:05 i-019a4b9bc446dddb4 systemd[1]: Starting OpenBSD Secure Shell server...
Apr 07 06:59:05 i-019a4b9bc446dddb4 sshd[1908]: Server listening on 0.0.0.0 port 22.
Apr 07 06:59:05 i-019a4b9bc446dddb4 sshd[1908]: Server listening on :: port 22.
Apr 07 06:59:05 i-019a4b9bc446dddb4 systemd[1]: Started OpenBSD Secure Shell server.
Apr 07 06:59:23 i-019a4b9bc446dddb4 sshd[1915]: Account client has expired
Apr 07 06:59:23 i-019a4b9bc446dddb4 sshd[1915]: Connection closed by invalid user client 127.0.0.1 port 40946 [preauth]
```

19. list dynamic dependencies of `sshd`

It depends on `libpam.so`.

```
admin@i-0c86da093dcd7792d:/etc/pam.d$ ldd `which sshd` | grep pam
        libpam.so.0 => /lib/x86_64-linux-gnu/libpam.so.0 (0x00007fc55e8ea000)
```

20. check PAM config for sshd

```
admin@i-0c86da093dcd7792d:/etc/pam.d$ cat sshd
# PAM configuration for the Secure Shell service

# Standard Un*x authentication.
@include common-auth

# Disallow non-root logins when /etc/nologin exists.
account    required     pam_nologin.so
```

21. check the `/etc/shadow`

- Field 3 means `Last password change (lastchanged)`
    - It is `19393`.
- Field 7 means `Inactive : The number of days after password expires that account is disabled.`
    - It is `0`.

This implies the account `client` is "disabled".

```
root@i-0c86da093dcd7792d:/home/admin/.ssh# cat /etc/shadow | grep client
client:!:19393:0:99999:7::0:
```

22. enable the account `client`

```
 root@i-0c86da093dcd7792d:/home/admin/.ssh# chage -E -1 client
root@i-0c86da093dcd7792d:/home/admin/.ssh# chage -l client
Last password change                                    : Feb 05, 2023
Password expires                                        : never
Password inactive                                       : never
Account expires                                         : never
Minimum number of days between password change          : 0
Maximum number of days between password change          : 99999
Number of days of warning before password expires       : 7
```

23. try `sudo -u client ssh client@localhost 'pwd'`

User client not allowed because account is locked.

```
admin@i-0c86da093dcd7792d:~/.ssh$ sudo -u client ssh client@localhost 'pwd'
client@localhost: Permission denied (publickey).
admin@i-0c86da093dcd7792d:~/.ssh$ sudo systemctl status sshd
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-07 07:57:25 UTC; 23s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 2369 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
   Main PID: 2370 (sshd)
      Tasks: 1 (limit: 524)
     Memory: 1.0M
        CPU: 41ms
     CGroup: /system.slice/ssh.service
             └─2370 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups

Apr 07 07:57:25 i-0c86da093dcd7792d systemd[1]: Starting OpenBSD Secure Shell server...
Apr 07 07:57:25 i-0c86da093dcd7792d sshd[2370]: Server listening on 0.0.0.0 port 22.
Apr 07 07:57:25 i-0c86da093dcd7792d sshd[2370]: Server listening on :: port 22.
Apr 07 07:57:25 i-0c86da093dcd7792d systemd[1]: Started OpenBSD Secure Shell server.
Apr 07 07:57:37 i-0c86da093dcd7792d sshd[2377]: User client not allowed because account is locked
Apr 07 07:57:37 i-0c86da093dcd7792d sshd[2377]: Connection closed by invalid user client 127.0.0.1 port 33270 [preauth]
```

24. unlock the `client` by updating its password

```
admin@i-0c86da093dcd7792d:~/.ssh$ sudo passwd -S client
client L 02/05/2023 0 99999 7 -1
admin@i-0c86da093dcd7792d:~/.ssh$ sudo passwd client
New password: 123
Retype new password: 123
passwd: password updated successfully
admin@i-0c86da093dcd7792d:~/.ssh$ sudo passwd -S client
client P 04/07/2025 0 99999 7 -1
```

25. check `client` account information

The account is configured to prevent logins.

```
admin@i-0c86da093dcd7792d:~/.ssh$ cat /etc/passwd | grep client
client:x:1001:1001::/home/client:/usr/sbin/nologin
```

26. allow shell access to `client` account

```
admin@i-0c86da093dcd7792d:~/.ssh$ sudo usermod -s /bin/bash client
admin@i-0c86da093dcd7792d:~/.ssh$ cat /etc/passwd | grep client
client:x:1001:1001::/home/client:/bin/bash
admin@i-0c86da093dcd7792d:~/.ssh$ sudo -u client ssh client@localhost 'pwd'
/home/client
```
