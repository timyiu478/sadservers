## "Monaco": Disappearing Trick

### Problem

https://sadservers.com/newserver/monaco

TIP: a developer worked on the web server code in this VM, using the same 'admin' account.

### Solution

1. try to curl

this hints us to send an HTTP POST request with correct password for getting a password that we want.

```
admin@i-054d3c4bfff4b2ba2:~$ curl localhost:5000

        <form method="POST">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password">
            <input type="submit" value="Submit">
        </form>
```

2. try a random password

```
    admin@i-054d3c4bfff4b2ba2curl -X POST -d "password=123" localhost:5000
Access denied!
```

3. found a v1 webserver.py based on tip

```
admin@i-054d3c4bfff4b2ba2:~$ git status
On branch master
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    webserver_v1.py
```

4. restore it and check the source code

This hints us to check the process's environment variable.

```
admin@i-054d3c4bfff4b2ba2:~$ cat webserver_v1.py 
from flask import Flask, request
import os

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        super_secret_password = os.environ.get('SUPERSECRETPASSWORD')

        if entered_password == super_secret_password:
            return 'Access granted!'
            # DO STUFF HERE

        return 'Access denied!'

    return '''
        <form method="POST">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password">
            <input type="submit" value="Submit">
        </form>
    '''


if __name__ == '__main__':
    app.run()
```

5. check process environment variables

SUPERSECRETPASSWORD=bdFBkE4suaCy

```
admin@i-054d3c4bfff4b2ba2:~$ ps -aux | grep web
admin        570  0.0  6.0 106768 28220 ?        Ss   13:28   0:00 /usr/bin/python3 /home/admin/webserver.py
admin       1625  0.0  0.1   5264   704 pts/3    S<+  13:59   0:00 grep web
admin@i-054d3c4bfff4b2ba2:~$ cat /proc/570/environ 
LANG=C.UTF-8PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binHOME=/home/adminLOGNAME=adminUSER=adminSHELL=/bin/bashINVOCATION_ID=ab5627b581ce464086895243c2bf5889JOURNAL_STREAM=8:11365SUPERSECRETPASSWORD=bdFBkE4suaCy
```

6. try the password `bdFBkE4suaCy`

```
admin@i-054d3c4bfff4b2ba2:~$ curl -X POST -d "password=bdFBkE4suaCy" localhost:5000
Access granted! Secret is QhyjuI98BBvfadmin@i-054d3c4bfff4b2ba2:~$ 
```
