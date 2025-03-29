## "Bucharest": Connecting to Postgres

### Problem

> A web application relies on the PostgreSQL 13 database present on this server. However, the connection to the database is not working. Your task is to identify and resolve the issue causing this connection failure. The application connects to a database named app1 with the user app1user and the password app1user.

https://sadservers.com/scenario/bucharest

### Solution

1. try to connect and see whether will return some useful error response

```
admin@i-0a35c3f8417dc63d8:~$ PGPASSWORD=app1user psql -h 127.0.0.1 -d app1 -U app1user -c '\q'
psql: error: FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL on
FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL off
```

2. check the `pg_hba.conf`

```
admin@i-0a35c3f8417dc63d8:/etc/postgresql/13/main$ sudo vim pg_hba.conf
```

```
# Database administrative login by Unix domain socket
local   all             postgres                                peer
host    all             all             all                     reject
host    all             all             all                     reject

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     peer
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     peer
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5
```

3. check the postgresql log

```
admin@i-0a35c3f8417dc63d8:/var/log/postgresql$ tail postgresql-13-main.log 
2023-11-25 18:05:24.184 UTC [1454] LOG:  background worker "logical replication launcher" (PID 1461) exited with exit code 1
2023-11-25 18:05:24.184 UTC [1456] LOG:  shutting down
2023-11-25 18:05:24.206 UTC [1454] LOG:  database system is shut down
2025-03-29 07:47:40.438 UTC [641] LOG:  starting PostgreSQL 13.13 (Debian 13.13-0+deb11u1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 10.2.1-6) 10.2.1 20210110, 64-bit
2025-03-29 07:47:40.439 UTC [641] LOG:  listening on IPv4 address "127.0.0.1", port 5432
2025-03-29 07:47:40.443 UTC [641] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
2025-03-29 07:47:40.461 UTC [645] LOG:  database system was shut down at 2023-11-25 18:05:24 UTC
2025-03-29 07:47:40.478 UTC [641] LOG:  database system is ready to accept connections
2025-03-29 07:49:04.646 UTC [899] app1user@app1 FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL on
2025-03-29 07:49:04.648 UTC [900] app1user@app1 FATAL:  pg_hba.conf rejects connection for host "127.0.0.1", user "app1user", database "app1", SSL off
```

4. comment the config the rejects connect from all user to all addresses in `pg_hba.conf`

```
# host    all             all             all                     reject
# host    all             all             all                     reject
```

5. reload the postgresql

```
admin@i-0a35c3f8417dc63d8:/etc/postgresql/13/main$ sudo systemctl reload postgresql
admin@i-0a35c3f8417dc63d8:/etc/postgresql/13/main$ sudo systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
     Active: active (exited) since Sat 2025-03-29 07:47:42 UTC; 18min ago
    Process: 1324 ExecReload=/bin/true (code=exited, status=0/SUCCESS)
   Main PID: 673 (code=exited, status=0/SUCCESS)
        CPU: 1ms

Mar 29 07:47:42 i-0a35c3f8417dc63d8 systemd[1]: Starting PostgreSQL RDBMS...
Mar 29 07:47:42 i-0a35c3f8417dc63d8 systemd[1]: Finished PostgreSQL RDBMS.
Mar 29 08:06:14 i-0a35c3f8417dc63d8 systemd[1]: Reloading PostgreSQL RDBMS.
Mar 29 08:06:14 i-0a35c3f8417dc63d8 systemd[1]: Reloaded PostgreSQL RDBMS.
admin@i-0a35c3f8417dc63d8:/etc/postgresql/13/main$ PGPASSWORD=app1user psql -h 127.0.0.1 -d app1 -U app1user -c '\q'
admin@i-0a35c3f8417dc63d8:/etc/postgresql/13/main$ 
```
