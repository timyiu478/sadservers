## "Depok": Nginx with Brotli

### Problem

You are tasked to add compression to the company website. The website is running on an Nginx server, and you decide to add [Brotli compression](https://en.wikipedia.org/wiki/Brotli) to it.

Brotli has became very popular these days because of its high compression ratio. It's a generic-purpose lossless compression algorithm that compresses data using a combination of a modern variant of the LZ77 algorithm, Huffman coding, and 2nd order context modeling.

For this purpose, you decided to compile the brotli modules yourself and add them to the Nginx server.

The location of the Brotli source code is at `/home/admin/ngx_brotli`. The nginx source code (needed to compile the modules) is located at `/home/admin/nginx-1.18.0`. From the [ngx_brotli](https://github.com/google/ngx_brotli) repository first you need to compile the brotli dependencies and then configure and make modules for Nginx. Afer that you need to add the modules to the Nginx configuration.

After installing the modules, you need to make sure the responses from the server are being server with compression.

Create a port-forward to port `80` from the server to your computer and check the header Content-Encoding, responses must return br for Brotli compression. You can also use `curl -H "Accept-Encoding: br, gzip" -I http://localhost` to check the header.

Something nice about Brotli is that it fails over to gzip if the client doesn't support Brotli, so `curl -H "Accept-Encoding: gzip" -I http://localhost` should return gzip instead.

Source: https://sadservers.com/scenario/depok

### Solution

1. uncompress nginx

```
admin@i-062185486addf85ae:~$ tar -xf nginx-1.18.0.tar.gz
```

2. check the nginx status

```
$ systemctl status nginx
admin@i-00ea2f0da8db2e4bb:/etc/nginx$ systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2025-04-04 10:50:08 UTC; 19min ago
       Docs: man:nginx(8)
   Main PID: 620 (nginx)
      Tasks: 3 (limit: 521)
     Memory: 8.5M
        CPU: 48ms
     CGroup: /system.slice/nginx.service
             ├─620 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─621 nginx: worker process
             └─622 nginx: worker process

Apr 04 10:50:08 i-00ea2f0da8db2e4bb systemd[1]: Starting A high performance web server and a reverse proxy server...
Apr 04 10:50:08 i-00ea2f0da8db2e4bb systemd[1]: Started A high performance web server and a reverse proxy server.
```

3. install dependencies of `brotli` using dynamically load approach

follow this guide: https://github.com/google/ngx_brotli?tab=readme-ov-file#statically-compiled

remarks:

1. change `/path/to/ngx_brotli` to `/home/admin/ngx_brotli`
2. remember to add the sample configuration in `/etc/nginx/nginx.conf`

```
brotli on;
brotli_comp_level 6;
brotli_static on;
brotli_types application/atom+xml application/javascript application/json application/vnd.api+json application/rss+xml
             application/vnd.ms-fontobject application/x-font-opentype application/x-font-truetype
             application/x-font-ttf application/x-javascript application/xhtml+xml application/xml
             font/eot font/opentype font/otf font/truetype image/svg+xml image/vnd.microsoft.icon
             image/x-icon image/x-win-bitmap text/css text/javascript text/plain text/xml;
```

4. reload the nginx config

```
admin@i-0245714a45adefcb7:/usr/sbin$ sudo systemctl reload nginx
admin@i-0245714a45adefcb7:/usr/sbin$ systemctl status nginx
● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2025-04-04 11:22:21 UTC; 7min ago
       Docs: man:nginx(8)
    Process: 3900 ExecReload=/usr/sbin/nginx -g daemon on; master_process on; -s reload (code=exited, status=0/SUCCESS)
   Main PID: 630 (nginx)
      Tasks: 3 (limit: 521)
     Memory: 12.1M
        CPU: 71ms
     CGroup: /system.slice/nginx.service
             ├─ 630 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             ├─3901 nginx: worker process
             └─3902 nginx: worker process

Apr 04 11:22:21 i-0245714a45adefcb7 systemd[1]: Starting A high performance web server and a reverse proxy server...
Apr 04 11:22:21 i-0245714a45adefcb7 systemd[1]: Started A high performance web server and a reverse proxy server.
Apr 04 11:28:33 i-0245714a45adefcb7 systemd[1]: Reloading A high performance web server and a reverse proxy server.
Apr 04 11:28:33 i-0245714a45adefcb7 systemd[1]: Reloaded A high performance web server and a reverse proxy server.
```

5. test

We can see the `Content-Encoding: br` header

```
admin@i-0245714a45adefcb7:/usr/sbin$ curl -H "Accept-Encoding: br" -sI http://localhost
HTTP/1.1 200 OK
Server: nginx/1.18.0
Date: Fri, 04 Apr 2025 11:33:58 GMT
Content-Type: text/html
Last-Modified: Sun, 14 Apr 2024 15:43:41 GMT
Connection: keep-alive
ETag: W/"661bf9ad-395a"
Content-Encoding: br
```
