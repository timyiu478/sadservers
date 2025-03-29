## "Manhattan": can't write data into database.

### Problem

https://sadservers.com/scenario/manhattan

### Solution

1. try to insert a row in postgres and see the error response

```
root@i-04360283c4f651af6:/# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory
        Is the server running locally and accepting connections on that socket?
```

2. check the status of postgresql

it was exited.

```
root@i-04360283c4f651af6:/etc/postgresql/14/main# systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (exited) since Sat 2025-03-29 14:40:52 UTC; 9min ago
 Main PID: 657 (code=exited, status=0/SUCCESS)
    Tasks: 0 (limit: 537)
   Memory: 0B
   CGroup: /system.slice/postgresql.service

Mar 29 14:40:52 i-04360283c4f651af6 systemd[1]: Starting PostgreSQL RDBMS...
Mar 29 14:40:52 i-04360283c4f651af6 systemd[1]: Started PostgreSQL RDBMS.
```

3. restart the postgresql is no help

```
root@i-04360283c4f651af6:/etc/postgresql/14/main# systemctl restart postgresql
root@i-04360283c4f651af6:/etc/postgresql/14/main# systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: active (exited) since Sat 2025-03-29 14:52:11 UTC; 1s ago
  Process: 13867 ExecStart=/bin/true (code=exited, status=0/SUCCESS)
 Main PID: 13867 (code=exited, status=0/SUCCESS)

Mar 29 14:52:11 i-04360283c4f651af6 systemd[1]: Starting PostgreSQL RDBMS...
Mar 29 14:52:11 i-04360283c4f651af6 systemd[1]: Started PostgreSQL RDBMS.
```

4. check its unit file

`/bin/true` is weird.

```
root@i-04360283c4f651af6:/etc/postgresql/14/main# systemctl cat postgresql
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
```

5. update postgres.service

```
root@i-04360283c4f651af6:/lib/systemd/system# cat postgresql.service 
# systemd service for managing all PostgreSQL clusters on the system. This
# service is actually a systemd target, but we are using a service since
# targets cannot be reloaded.

[Unit]
Description=PostgreSQL RDBMS

[Service]
User=postgres
Group=postgres
ExecStart=/usr/lib/postgresql/14/bin/postgres -c config_file=/etc/postgresql/14/main/postgresql.conf
ExecReload=/usr/lib/postgresql/14/bin/postgres -c config_file=/etc/postgresql/14/main/postgresql.conf
RemainAfterExit=on

[Install]
WantedBy=multi-user.target
```

6. restart service and check its status

FATAL: could not create lock file "postmaster.pid": No space

```
root@i-04360283c4f651af6:/lib/systemd/system# systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Sat 2025-03-29 15:06:33 UTC; 17s ago
  Process: 14338 ExecStart=/usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/14/main -c config_file=/etc/postgresql/14/main/postgresql.conf (
 Main PID: 14338 (code=exited, status=1/FAILURE)

Mar 29 15:06:33 i-04360283c4f651af6 systemd[1]: Started PostgreSQL RDBMS.
Mar 29 15:06:33 i-04360283c4f651af6 postgres[14338]: 2025-03-29 15:06:33.173 UTC [14338] FATAL:  could not create lock file "postmaster.pid": No space
Mar 29 15:06:33 i-04360283c4f651af6 systemd[1]: postgresql.service: Main process exited, code=exited, status=1/FAILURE
Mar 29 15:06:33 i-04360283c4f651af6 systemd[1]: postgresql.service: Failed with result 'exit-code'.
```

7. check the postgresql data directory 

```
root@i-04360283c4f651af6:/lib/systemd/system# cat /etc/postgresql/14/main/postgresql.conf | grep data_dir
#data_directory = '/var/lib/postgresql/14/main'         # use data in another directory
data_directory = '/opt/pgdata/main'             # use data in another director
```

8. check the disk usage in `/opt/pgdata`

Its 100% used.

```
root@i-04360283c4f651af6:/lib/systemd/system# df -h /opt/pgdata
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1    8.0G  8.0G   28K 100% /opt/pgdata
```

```
root@i-04360283c4f651af6:/lib/systemd/system# ls /opt/pgdata/ -alt
total 8285624
drwx------ 19 postgres postgres       4096 May 21  2022 main
-rw-r--r--  1 root     root         499712 May 21  2022 file3.bk
drwxr-xr-x  3 postgres postgres         82 May 21  2022 .
-rw-r--r--  1 root     root             69 May 21  2022 deleteme
-rw-r--r--  1 root     root      967774208 May 21  2022 file2.bk
-rw-r--r--  1 root     root     7516192768 May 21  2022 file1.bk
drwxr-xr-x  3 root     root           4096 May 21  2022 ..
```

9. remove `deleteme` and `file1.bk`

```
root@i-04360283c4f651af6:/lib/systemd/system# rm /opt/pgdata/deleteme
```

10. restart postgresql

This time it said: lock file "postmaster.pid" already exists

```
root@i-0e0e1d4d51c1af489:/opt/pgdata# systemctl status postgresql
● postgresql.service - PostgreSQL RDBMS
   Loaded: loaded (/lib/systemd/system/postgresql.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Sat 2025-03-29 15:46:39 UTC; 7s ago
  Process: 13879 ExecStart=/usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/14/main -c config_file=/etc/postgresql/14/main/postgresql.conf (
 Main PID: 13879 (code=exited, status=1/FAILURE)

Mar 29 15:46:39 i-0e0e1d4d51c1af489 systemd[1]: Started PostgreSQL RDBMS.
Mar 29 15:46:39 i-0e0e1d4d51c1af489 postgres[13879]: 2025-03-29 15:46:39.430 UTC [13879] FATAL:  lock file "postmaster.pid" already exists
Mar 29 15:46:39 i-0e0e1d4d51c1af489 postgres[13879]: 2025-03-29 15:46:39.430 UTC [13879] HINT:  Is another postmaster (PID 13861) running in data dire
Mar 29 15:46:39 i-0e0e1d4d51c1af489 systemd[1]: postgresql.service: Main process exited, code=exited, status=1/FAILURE
Mar 29 15:46:39 i-0e0e1d4d51c1af489 systemd[1]: postgresql.service: Failed with result 'exit-code'.
```

there is another postgresql running

```
root@i-0e0e1d4d51c1af489:/opt/pgdata/main# sudo -u postgres psql -c "insert into persons(name) values ('jane smith');" -d dt
INSERT 0 1
```
