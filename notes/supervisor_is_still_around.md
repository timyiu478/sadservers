## "Bekasi": Supervisor is still around

### Problem

There is an nginx service running on port 443, it is the main web server for the company and looks like a new employee has deployed some changes to the configuration of supervisor and now it is not working as expected.

If you try to access curl -k https://bekasi it should return Hello SadServers! but for some reason it is not.

You cannot modify files from the /home/admin/bekasi folder in order to pass the check.sh

You must find out what the issue is and fix it.

Ref: https://sadservers.com/scenario/bekasi

### Solution

1. try to curl

nginx seems work but bekasi does not.

```
admin@i-04482652e0c9160f5:/etc/supervisor/conf.d$ curl -vvv -k https://bekasi
< HTTP/1.1 200 OK
< Server: nginx/1.18.0
< Date: Tue, 22 Apr 2025 05:33:33 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 51
< Connection: keep-alive
< 
Failed to start the server. Please check the setup
* Connection #0 to host bekasi left intact
```


2. check bekasi logs

the server can receive http requests and return http responses

```
admin@i-04482652e0c9160f5:/var/log$ tail bekasi.log 
WSGI app 0 (mountpoint='') ready in 1 seconds on interpreter 0x5608d7616bd0 pid: 776 (default app)
*** uWSGI is running in multiple interpreter mode ***
spawned uWSGI master process (pid: 776)
spawned uWSGI worker 1 (pid: 903, cores: 1)
spawned uWSGI worker 2 (pid: 904, cores: 1)
spawned uWSGI worker 3 (pid: 905, cores: 1)
spawned uWSGI worker 4 (pid: 906, cores: 1)
spawned uWSGI worker 5 (pid: 907, cores: 1)
[pid: 906|app: 0|req: 1/1] 127.0.0.1 () {34 vars in 350 bytes} [Tue Apr 22 05:22:05 2025] GET / => generated 51 bytes in 15 msecs (HTTP/1.1 200) 2 headers in 79 bytes (1 switches on core 0)
[pid: 906|app: 0|req: 2/2] 127.0.0.1 () {34 vars in 350 bytes} [Tue Apr 22 05:33:33 2025] GET / => generated 51 bytes in 0 msecs (HTTP/1.1 200) 2 headers in 79 bytes (2 switches on core 0)
```

3. check the http server source code

We have to set BEKASI_SERVER and BEKASI_USER. 

```
admin@i-04482652e0c9160f5:~/bekasi$ cat bekasi.py
import os
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    if check_env():
        return "Hello SadServers!\n"
    else:
        return "Failed to start the server. Please check the setup\n"

def check_env():
    isServerSet = os.getenv('BEKASI_SERVER')
    isUserSet = os.getenv('BEKASI_USER')
    return isServerSet and isUserSet

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)a
```

4. set environment variables

```
admin@i-0701e20a7342765f3:/etc/supervisor/conf.d$ cat uwsgi.conf 
environment=BEKASI_SERVER="3",BEKASI_USER="4"
```

5. let supervisor reload the updated config and restart bekasi

```
admin@i-0701e20a7342765f3:/etc/supervisor/conf.d$ sudo supervisorctl reread
bekasi: changed
admin@i-0701e20a7342765f3:/etc/supervisor/conf.d$ sudo supervisorctl update
bekasi: stopped
bekasi: updated process group
admin@i-0701e20a7342765f3:/etc/supervisor/conf.d$ sudo supervisorctl restart bekasi
bekasi: stopped
bekasi: started
```

6. try to curl

```
admin@i-0701e20a7342765f3:/etc/supervisor/conf.d$ curl -k https://bekasi
Hello SadServers!
```
