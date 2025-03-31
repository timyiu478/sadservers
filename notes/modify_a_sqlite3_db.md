## "Atrani": Modify a SQlite3 Database

### Problem

> A developer created a script /home/admin/readdb.py that tests access to a database. Without modifying the readdb.py file, change the database so that running the script returns the string "John Karmack".

https://sadservers.com/scenario/atrani

### Solution


1. read the `readdb.py` to know where is the database file and what is the query

```
admin@i-0a0a2f8eb0551da12:~$ cat readdb.py 
#!/usr/bin/python3

import sqlite3
import os


def read_db():
    db_file = os.environ.get('DB_FILE')
    if not db_file:
        db_file = '/home/admin/users.db'
        if not os.path.exists(db_file):
            print('Database file not found')
            return 1

    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    try:
        c.execute('SELECT name, timestamp FROM users where id = 1')
    except Exception as e:
        print(f"Database execution error: {e}")
        return 1
    print(c.fetchall()[0][0])
    conn.close()


read_db()
```

2. create new db file and set environment variable `DB_FILE` refers to it because `users.db` is read only

```
admin@i-0a0a2f8eb0551da12:~$ touch new_users.db
admin@i-0a0a2f8eb0551da12:~$ export DB_FILE=new_users.db
```

3. run sqlite3

4. create users table

```
sqlite> create table users(name text, timestamp int, id int);
```

5. insert user into users and save `new_users.db`

```
sqlite> insert into users values('John Karmack', 1, 1);
sqlite> select * from users;
John Karmack|1|1
sqlite> .save new_users.db;
```

6. check the `check.sh` and found the `/etc/profile` will override the environment variable `DB_FILE`

```
admin@i-0d12db8b6bfb94ba0:~$ cat agent/check.sh 
#!/usr/bin/bash
# DO NOT MODIFY THIS FILE ("Check My Solution" will fail)

res=$(md5sum /home/admin/readdb.py |awk '{print $1}')
res=$(echo $res|tr -d '\r')

if [[ "$res" != "c4d5e1d8c4efbd3b70ab5569e2058157" ]]
then
  echo -n "NO"
  exit 1
fi

source /etc/profile
res=$(/home/admin/readdb.py)

if [[ "$res" = "John Karmack" ]]
then
  echo -n "OK"
else
  echo -n "NO"
fi
```

```
admin@i-0d12db8b6bfb94ba0:~$ cat /etc/profile
...
export DB_FILE="/opt/users.db"
```

7. we have permission to write `/opt/users.db`

```
admin@i-0d12db8b6bfb94ba0:~$ ls /opt/users.db -alt
-rwxr-xr-x 1 admin admin 8192 Aug 25  2024 /opt/users.db
```

8. view `/opt/users.db`

the users table schema are different

```
sqlite> .open /opt/users.db
sqlite> .mode table
sqlite> select * from users;
+----+--------------+-------+
| id |     name     | email |
+----+--------------+-------+
| 1  | John Karmack |       |
+----+--------------+-------+
sqlite> .schema
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
);
```

9. update `/opt/users.db`

```
sqlite> drop table users;
sqlite> create table users(name text, timestamp int, id int);
sqlite> insert into users values('John Karmack', 1, 1);
sqlite> .save /opt/users.db
```
