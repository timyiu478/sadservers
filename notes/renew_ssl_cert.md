## "Geneva": Renew an SSL Certificate

### Problem

https://sadservers.com/newserver/geneva

### Solution

1. find the nginx Certificate location

```
/etc/nginx/ssl/
```

2. read the Certificate in plaintext to 

```
admin@i-08c89f6b49c8cce62:/etc/nginx/ssl$ sudo openssl x509 -in nginx.crt -text -out cert.txt
```

```
CN = localhost
O = Acme
OU = IT Department
L = Geneva
ST = Geneva
C = CH
```

3. generate new Certificate signing request

```
admin@i-0ba311c1140246e56:/etc/nginx/ssl$ sudo openssl req -new -key nginx.key -out new.csr
```

4. renew self signed request

```
admin@i-08dd3071f7da52353:/etc/nginx/ssl$ sudo openssl x509 -req -days 365 -in new.csr -signkey nginx.key -out renewed_certificate.crt
```

5. back up the original `nginx.crt`

```
admin@i-08dd3071f7da52353:/etc/nginx/ssl$ sudo cp nginx.crt nginx_bak.crt
```

6. update nginx ssl certificate path

```
server {
    listen 443 ssl;
    ssl_certificate renewed_certificate.crt;
    ssl_certificate_key nginx.key;

    # Other configuration settings...
}
```

7. test the configuration update

```
admin@i-08dd3071f7da52353:/etc/nginx/sites-enabled$ sudo nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

8. restart the nginx daemon

```
admin@i-08dd3071f7da52353:/etc/nginx/sites-enabled$ systemctl status nginx.service
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Sat 2025-03-29 06:49:53 UTC; 14min ago
       Docs: man:nginx(8)
    Process: 990 ExecReload=/usr/sbin/nginx -g daemon on; master_process on; -s reload (code=exited, status=0/SUCCESS)
   Main PID: 631 (nginx)
      Tasks: 3 (limit: 522)
     Memory: 13.1M
        CPU: 92ms
     CGroup: /system.slice/nginx.service
             ├─631 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─991 nginx: worker process
             └─992 nginx: worker process

Mar 29 06:49:53 i-08dd3071f7da52353 systemd[1]: Starting A high performance web server and a reverse proxy server...
Mar 29 06:49:53 i-08dd3071f7da52353 systemd[1]: Started A high performance web server and a reverse proxy server.
Mar 29 07:04:35 i-08dd3071f7da52353 systemd[1]: Reloading A high performance web server and a reverse proxy server.
Mar 29 07:04:35 i-08dd3071f7da52353 systemd[1]: Reloaded A high performance web server and a reverse proxy server.
```

9. 

Test: Certificate should not be expired: `echo | openssl s_client -connect localhost:443 2>/dev/null | openssl x509 -noout -dates` and the subject of the certificate should be the same as the original one: `echo | openssl s_client -connect localhost:443 2>/dev/null | openssl x509 -noout -subject`
