## "Hong-Kong": can't write data into database.

### Problem

Your objective is to be able to insert a row in an existing Postgres database. The issue is not specific to Postgres and you don't need to know details about it (although it may help).

Postgres information: it's a service that listens to a port (:5432) and writes to disk in a data directory, the location of which is defined in the data_directory parameter of the configuration file /etc/postgresql/14/main/postgresql.conf. In our case Postgres is managed by systemd as a unit with name postgresql.

https://sadservers.com/scenario/hongkong

### Solution

1. try `sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt`

```
root@i-04504ca3f5b61d22b:/# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
        Is the server running locally and accepting connections on that socket?
```

2. check the status of `postgresql`

```
root@i-04504ca3f5b61d22b:/# systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (exited) since Sat 2025-04-19 14:43:00 UTC; 2min 41s ago
 Main PID: 589 (code=exited, status=0/SUCCESS)
    Tasks: 0 (limit: 535)
   Memory: 0B
   CGroup: /system.slice/postgresql.service

Apr 19 14:43:00 i-04504ca3f5b61d22b systemd[1]: Starting PostgreSQL RDBMS...
Apr 19 14:43:00 i-04504ca3f5b61d22b systemd[1]: Started PostgreSQL RDBMS.
root@i-04504ca3f5b61d22b:/# systemctl cat postgresql
# /lib/systemd/system/postgresql.service
# systemd service for managing all PostgreSQL clusters on the system. This
# service is actually a systemd target, but we are using a service since
# targets cannot be reloaded.

[Unit]
Description=PostgreSQL RDBMS

[Service]
Type=oneshot
ExecStart=/bin/true
ExecReload=/bin/true
RemainAfterExit=on

[Install]
WantedBy=multi-user.target
root@i-04504ca3f5b61d22b:/#
```

3. update the postgresql unit file

```
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# sudo systemctl cat postgresql
# /lib/systemd/system/postgresql.service
# systemd service for managing all PostgreSQL clusters on the system. This
# service is actually a systemd target, but we are using a service since
# targets cannot be reloaded.

[Unit]
Description=PostgreSQL RDBMS
After=network.target

[Service]
Type=notify
User=postgres
ExecStart=/usr/lib/postgresql/14/bin/postgres -c config_file=/etc/postgresql/14/main/postgresql.conf
ExecReload=/bin/kill -HUP $MAINPID

[Install]
WantedBy=multi-user.target
```

4. restart postgres and check its status

```
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# sudo systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Sat 2025-04-19 14:55:03 UTC; 1min 22s ago
  Process: 14734 ExecStart=/usr/lib/postgresql/14/bin/postgres -c config_file=/etc/postgresql/14/main/postgresql.conf (code=exited, status=1/FAILURE)
 Main PID: 14734 (code=exited, status=1/FAILURE)

Apr 19 14:55:03 i-04504ca3f5b61d22b systemd[1]: Starting PostgreSQL RDBMS...
Apr 19 14:55:03 i-04504ca3f5b61d22b postgres[14734]: 2025-04-19 14:55:03.535 GMT [14734] LOG:  skipping missing configuration file "/opt/pgdata/main/p
Apr 19 14:55:03 i-04504ca3f5b61d22b postgres[14734]: 2025-04-19 14:55:03.535 UTC [14734] FATAL:  data directory "/opt/pgdata/main" does not exist
Apr 19 14:55:03 i-04504ca3f5b61d22b systemd[1]: postgresql.service: Main process exited, code=exited, status=1/FAILURE
Apr 19 14:55:03 i-04504ca3f5b61d22b systemd[1]: postgresql.service: Failed with result 'exit-code'.
Apr 19 14:55:03 i-04504ca3f5b61d22b systemd[1]: Failed to start PostgreSQL RDBMS.
```

5. update the data directory to `/var/lib/postgresql/14/main`

```
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# ls -alt /var/lib/postgresql/14/main
total 88
drwx------ 19 postgres postgres 4096 May 21  2022 .
drwx------  2 postgres postgres 4096 May 21  2022 pg_stat
drwx------  4 postgres postgres 4096 May 21  2022 pg_logical
drwx------  2 postgres postgres 4096 May 21  2022 global
-rw-------  1 postgres postgres  130 May 21  2022 postmaster.opts
drwx------  5 postgres postgres 4096 May 21  2022 base
drwx------  2 postgres postgres 4096 May 21  2022 pg_subtrans
drwx------  3 postgres postgres 4096 May 21  2022 pg_wal
drwx------  2 postgres postgres 4096 May 21  2022 pg_xact
-rw-------  1 postgres postgres   88 May 21  2022 postgresql.auto.conf
-rw-------  1 postgres postgres    3 May 21  2022 PG_VERSION
drwx------  2 postgres postgres 4096 May 21  2022 pg_stat_tmp
drwx------  2 postgres postgres 4096 May 21  2022 pg_commit_ts
drwx------  2 postgres postgres 4096 May 21  2022 pg_dynshmem
drwx------  4 postgres postgres 4096 May 21  2022 pg_multixact
drwx------  2 postgres postgres 4096 May 21  2022 pg_notify
drwx------  2 postgres postgres 4096 May 21  2022 pg_replslot
drwx------  2 postgres postgres 4096 May 21  2022 pg_serial
drwx------  2 postgres postgres 4096 May 21  2022 pg_snapshots
drwx------  2 postgres postgres 4096 May 21  2022 pg_tblspc
drwx------  2 postgres postgres 4096 May 21  2022 pg_twophase
drwxr-xr-x  3 postgres postgres 4096 May 21  2022 ..
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# cat /etc/postgresql/14/main/postgresql.conf | grep data_d
#data_directory = '/var/lib/postgresql/14/main'         # use data in another directory
data_directory = '/opt/pgdata/main'             # use data in another directory
```

6. try to insert row into database `dt`

```
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  database "dt" does not exist
```

7. create database `dt` and table `persons`

```
root@i-04504ca3f5b61d22b:/usr/lib/postgresql/14# sudo -u postgres psql
psql (14.3 (Debian 14.3-1.pgdg100+1))
Type "help" for help.

postgres=# CREATE DATABASE dt;
CREATE DATABASE
postgres=# \c dt
You are now connected to database "dt" as user "postgres".
dt=# CREATE TABLE persons (
dt(#     name VARCHAR(255)
dt(# );
CREATE TABLE
dt=# \d
          List of relations
 Schema |  Name   | Type  |  Owner   
--------+---------+-------+----------
 public | persons | table | postgres
(1 row)

dt=# \d persons
                      Table "public.persons"
 Column |          Type          | Collation | Nullable | Default 
--------+------------------------+-----------+----------+---------
 name   | character varying(255) |           |          | 
```
