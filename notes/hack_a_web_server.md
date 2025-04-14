## "Roseau": Hack a Web Server

### Problem

There is a secret stored in a file that the local Apache web server can provide. Find this secret and have it as a /home/admin/secret.txt file.

Note that in this server the admin user is not a sudoer.

Also note that the password crackers Hashcat and Hydra are installed from packages and John the Ripper binaries have been built from source in /home/admin/john/run

https://sadservers.com/newserver/roseau

### Solution

1. check the status of the web server

```
admin@i-0395efb13f3c29910:/$ systemctl status apache2
● apache2.service - The Apache HTTP Server
     Loaded: loaded (/lib/systemd/system/apache2.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-14 12:40:11 UTC; 1min 22s ago
       Docs: https://httpd.apache.org/docs/2.4/
   Main PID: 638 (apache2)
      Tasks: 55 (limit: 524)
     Memory: 7.6M
        CPU: 111ms
     CGroup: /system.slice/apache2.service
             ├─638 /usr/sbin/apache2 -k start
             ├─736 /usr/sbin/apache2 -k start
             └─737 /usr/sbin/apache2 -k start

Apr 14 12:40:11 i-0395efb13f3c29910 systemd[1]: Starting The Apache HTTP Server...
Apr 14 12:40:11 i-0395efb13f3c29910 systemd[1]: Started The Apache HTTP Server.
Apr 14 12:40:11 i-0395efb13f3c29910 systemd[1]: Reloading The Apache HTTP Server.
Apr 14 12:40:12 i-0395efb13f3c29910 systemd[1]: Reloaded The Apache HTTP Server.
```

2. check web server unit file

```
admin@i-0395efb13f3c29910:/$ systemctl cat apache2
# /lib/systemd/system/apache2.service
[Unit]
Description=The Apache HTTP Server
After=network.target remote-fs.target nss-lookup.target
Documentation=https://httpd.apache.org/docs/2.4/

[Service]
Type=forking
Environment=APACHE_STARTED_BY_SYSTEMD=true
ExecStart=/usr/sbin/apachectl start
ExecStop=/usr/sbin/apachectl graceful-stop
ExecReload=/usr/sbin/apachectl graceful
KillMode=mixed
PrivateTmp=true
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

3. cant see which socket the web server bind and listen on using `netstat`

```
admin@i-0395efb13f3c29910:/$ netstat -tnclp 
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::6767                 :::*                    LISTEN      589/sadagent        
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::8080                 :::*                    LISTEN      588/gotty           
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
tcp6       0      0 :::34301                :::*                    LISTEN      -                   
tcp6       0      0 :::42559                :::*                    LISTEN      -  
```

4. check web server configs

- It serves files from `/var/www/html`.
- no read permission on `/var/www/html/webfile`.
- be able to read `/etc/apache2/.htpasswd`

```
admin@i-0395efb13f3c29910:/etc/apache2/sites-enabled$ cat 000-default.conf 
<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined


        <Directory "/var/www/html">
                AuthType Basic
                AuthName "Protected Content"
                AuthUserFile /etc/apache2/.htpasswd
                Require valid-user
        </Directory>
</VirtualHost>
admin@i-0395efb13f3c29910:/etc/apache2/sites-enabled$ ls -alt /var/www/html
total 12
drwxr-xr-x 2 root     root     4096 Feb 13  2023 .
-rw-r----- 1 www-data www-data  215 Feb 13  2023 webfile
drwxr-xr-x 3 root     root     4096 Feb 13  2023 ..
admin@i-0395efb13f3c29910:/etc/apache2$ cat .htpasswd 
carlos:$apr1$b1kyfnHB$yRHwzbuKSMyW62QTnGYCb0
```

5. try to crack the hashed password using the tools

- `-m 1600`: select apache hash type
- `-a 0`: attacker mode is dictionary

Got `Initializing backend runtime for device #1...Killed`

```
admin@i-0c55eb3bea7a0cb42:~$ cat hpw 
admin@i-0c55eb3bea7a0cb42:~$ hashcat -m 1600 -a 0 -o result hpw
Initializing backend runtime for device #1...Killed
```

6. try to use `john` instead of `hashcat` 

```
admin@i-06212d9a705f99ce9:~/john/run$ ./john -w:password.lst ~/htp 
Warning: detected hash type "md5crypt", but the string is also recognized as "md5crypt-long"
Use the "--format=md5crypt-long" option to force loading these as that type instead
Using default input encoding: UTF-8
Loaded 1 password hash (md5crypt, crypt(3) $1$ (and variants) [MD5 256/256 AVX2 8x3])
Will run 2 OpenMP threads
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
chalet           (?)     
1g 0:00:00:01 DONE (2025-04-14 15:22) 0.6622g/s 43358p/s 43358c/s 43358C/s 050381..song
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

7. try the cracked password

```
admin@i-06212d9a705f99ce9:/etc/apache2$ curl -u carlos:chalet localhost
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /</title>
 </head>
 <body>
<h1>Index of /</h1>
  <table>
   <tr><th valign="top"><img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a href="?C=D;O=A">Description</a></th></tr>
   <tr><th colspan="5"><hr></th></tr>
<tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="webfile">webfile</a></td><td align="right">2023-02-13 02:39  </td><td align="right">215 </td><td>&nbsp;</td></tr>
   <tr><th colspan="5"><hr></th></tr>
</table>
<address>Apache/2.4.54 (Debian) Server at localhost Port 80</address>
</body></html>
```

8. get the `webfile`

its a binary file.


Hint from AI: 

> This output seems to be a fragment of a compressed file (e.g., .zip) or binary data. The text includes patterns such as PK (which denotes the ZIP file format signature) and references to secret.txt, likely indicating that the file contains a specific text file named "secret.txt."

dont know the zip file password.


```
admin@i-06212d9a705f99ce9:~$ curl -u carlos:chalet http://localhost/webfile --output out
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   215  100   215    0     0   209k      0 --:--:-- --:--:-- --:--:--  209k
admin@i-06212d9a705f99ce9:~$ cat -A out 
PK^C^D$
^@^I^@^@^@M-`^TMVM-/M-iM-FM-*^]^@^@^@^Q^@^@^@$
^@^\^@secret.txtUT^I^@^CM-CM-"M-icM-CM-"M-icux^K^@^A^D^@^@^@^@^D^@^@^@^@s^GM-8^IM-BM-^]^NF^Bw^D(M-xM-tiM-:DM-^?M-^X^FXUM-eWM-wn)M-hM-QPK^G^HM-/M-iM-FM-*^]^@^@^@^Q^@^@^@PK^A^B^^^C$
^@^I^@^@^@M-`^TMVM-/M-iM-FM-*^]^@^@^@^Q^@^@^@$
^@^X^@^@^@^@^@^A^@^@^@M-$M-^A^@^@^@^@secret.txtUT^E^@^CM-CM-"M-icux^K^@^A^D^@^@^@^@^D^@^@^@^@PK^E^F^@^@^@^@^A^@^A^@P^@^@^@q^@^@^@^@^@
05f99ce9:~$ unzip out
Archive:  out
[out] secret.txt password: 
password incorrect--reenter: 
password incorrect--reenter: 
   skipping: secret.txt              incorrect password
```

9. `john` again

zip file password is `andes`.

```
admin@i-06212d9a705f99ce9:~/john/run$ ./zip2john ~/out > ~/unzipp
ver 1.0 efh 5455 efh 7875 out/secret.txt PKZIP Encr: 2b chk, TS_chk, cmplen=29, decmplen=17, crc=AAC6E9AF ts=14E0 cs=14e0 type=0
admin@i-06212d9a705f99ce9:~/john/run$ cd ~
admin@i-06212d9a705f99ce9:~$ ls
agent  htp  john  out  unzipp
admin@i-06212d9a705f99ce9:~$ cat unzipp 
out/secret.txt:$pkzip$1*2*2*0*1d*11*aac6e9af*0*44*0*1d*14e0*7307b809c29d0e4602770428f8f469ba44ff98065855e557f76e29e8d1*$/pkzip$:secret.txt:out::/home/admin/ou
admin@i-06212d9a705f99ce9:~/john/run$ ./john ~/unzipp 
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 2 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
Almost done: Processing the remaining buffered candidate passwords, if any.
0g 0:00:00:00 DONE 1/3 (2025-04-14 15:44) 0g/s 656800p/s 656800c/s 656800C/s Txtout1900..Tsecret1900
Proceeding with wordlist:./password.lst
Enabling duplicate candidate password suppressor
andes            (out/secret.txt)     
1g 0:00:00:00 DONE 2/3 (2025-04-14 15:44) 2.222g/s 1250Kp/s 1250Kc/s 1250KC/s poussinet..nisa1234
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

10. unzip it

```
admin@i-06212d9a705f99ce9:~$ unzip out
Archive:  out
[out] secret.txt password: 
 extracting: secret.txt              
admin@i-06212d9a705f99ce9:~$ ls
agent  htp  john  out  secret.txt  unzipp
admin@i-06212d9a705f99ce9:~$ cat secret.txt 
Roseau, Dominica
```
