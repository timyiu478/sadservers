## "Helsingør": The first walls of postgres physical replication

### Problem

https://sadservers.com/scenario/helsingor

### Solution

1. check the status of the running containers

one postgres up and one is restarting

```
admin@i-07b8aa3662d0646a7:~$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                          PORTS                                       NAMES
98e1b8d4a341   postgres:16   "docker-entrypoint.s…"   11 months ago   Restarting (1) 43 seconds ago                                               postgres-db-replica
e3810a53aa68   postgres:16   "docker-entrypoint.s…"   11 months ago   Up 2 minutes (healthy)          0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   postgres-db-master
```

2. check the docker-compose

The replicas are shared the same container network so they are not use the same port `5432`.

```
admin@i-07b8aa3662d0646a7:~$ cat docker-compose.yml 
version: '3.9'
x-pg-common:
  &pg-common
  image: postgres:16
  user: postgres
  restart: always
  healthcheck:
    test: "pg_isready -U helsingor -d postgres"
    interval: 30s
    timeout: 10s
    retries: 5

services:
  postgres-db-master:
    <<: *pg-common
    container_name: postgres-db-master
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: helsingor
      POSTGRES_PASSWORD: helsingor123
      POSTGRES_HOST_AUTH_METHOD: "scram-sha-256\nhost replication all 0.0.0.0/0 trust"
    volumes:
      - ./postgres/master/postgres.conf:/etc/postgresql/16/main/postgresql.conf
      - postgres-db-master-data:/var/lib/postgresql/data
      - ./postgres/master/initdb.d:/docker-entrypoint-initdb.d
    networks:
      - pg-net
    command: |
      postgres -c 'config_file=/etc/postgresql/16/main/postgresql.conf'
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 100M

  postgres-db-replica:
    <<: *pg-common
    container_name: postgres-db-replica
    ports:
      - 5433:5432
    environment:
      POSTGRES_PASSWORD: r3pl1c4t0r
    volumes:
      - ./postgres/replica/postgres.conf:/etc/postgresql/16/main/postgresql.conf
    networks:
      - pg-net
    command: |
      bash -c "
      rm -fR /var/lib/postgresql/data/
      until pg_basebackup -D /var/lib/postgresql/data -RP -X stream -c fast -S replicator_slot -U replication -p 5432 -h postgres-db-master
      do
        echo 'Waiting for primary to connect...'
        sleep 1s
      done
      echo 'Backup done, starting replica...'
      chmod 0700 /var/lib/postgresql/data
      touch /var/lib/postgresql/data/standby.signal
      postgres -c 'config_file=/etc/postgresql/16/main/postgresql.conf'
      "
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 100M
    depends_on:
      - postgres-db-master

networks:
  pg-net:
    driver: bridge

volumes:
  postgres-db-master-data:
```

3. change the replica's container network port to `5433` and restart it

4. check its status

Its still keep restarting

```
admin@i-07b8aa3662d0646a7:~/postgres/replica$ docker ps
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                         PORTS                                       NAMES
58330f22e59d   postgres:16   "docker-entrypoint.s…"   7 minutes ago   Restarting (1) 3 seconds ago                                               postgres-db-replica
8643145a9dc3   postgres:16   "docker-entrypoint.s…"   7 minutes ago   Up 7 minutes (healthy)         0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   postgres-db-master
```

5. check its logs

FATAL:  recovery aborted because of insufficient parameter settings
DETAIL:  max_connections = 80 is a lower setting than on the primary server, where its value was 100.

```
2025-04-01 07:23:11.516 GMT [1] LOG:  starting PostgreSQL 16.2 (Debian 16.2-1.pgdg120+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
2025-04-01 07:23:11.516 GMT [1] LOG:  listening on IPv4 address "0.0.0.0", port 5433
2025-04-01 07:23:11.516 GMT [1] LOG:  listening on IPv6 address "::", port 5433
2025-04-01 07:23:11.522 GMT [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5433"
2025-04-01 07:23:11.531 GMT [14] LOG:  database system was interrupted; last known up at 2025-04-01 07:23:10 GMT
2025-04-01 07:23:11.549 GMT [14] LOG:  entering standby mode
2025-04-01 07:23:11.549 GMT [14] LOG:  starting backup recovery with redo LSN 0/44000028, checkpoint LSN 0/44000060, on timeline ID 1
2025-04-01 07:23:11.555 GMT [14] FATAL:  recovery aborted because of insufficient parameter settings
2025-04-01 07:23:11.555 GMT [14] DETAIL:  max_connections = 80 is a lower setting than on the primary server, where its value was 100.
2025-04-01 07:23:11.555 GMT [14] HINT:  You can restart the server after making the necessary configuration changes.
2025-04-01 07:23:11.557 GMT [1] LOG:  startup process (PID 14) exited with exit code 1
2025-04-01 07:23:11.557 GMT [1] LOG:  aborting startup due to startup process failure
2025-04-01 07:23:11.557 GMT [1] LOG:  database system is shut down
admin@i-07b8aa3662d0646a7:~/postgres/replica$ docker ps
```

6. change `max_connections` to 100

```
admin@i-07b8aa3662d0646a7:~/postgres/replica$ cat postgres.conf | grep max_conn
max_connections = 100                   # (change requires restart)
```

7. restart container and check the log

```
2025-04-01 07:32:57.305 GMT [14] DETAIL:  max_worker_processes = 4 is a lower setting than on the primary server, where its value was 8.
```

8. update `max_worker_processes` to `8`

9. diff master/postgres.conf replica/postgres.conf

`max_wal_senders` and `max_locks_per_transaction` may have to change as well.

```
admin@i-07b8aa3662d0646a7:~/postgres$ diff master/postgres.conf replica/postgres.conf 
64c64
< port = 5432                           # (change requires restart)
---
> port = 5433                           # (change requires restart)
258c258
< archive_mode = on             # enables archiving; off, on, or always
---
> #archive_mode = off           # enables archiving; off, on, or always
314c314
< max_wal_senders = 10          # max number of walsender processes
---
> max_wal_senders = 5           # max number of walsender processes
338,339c338,339
< #primary_slot_name = ''                       # replication slot on sending server
< #hot_standby = on                     # "off" disallows queries during recovery
---
> #primary_slot_name = 'replicator'                     # replication slot on sending server
> hot_standby = on                      # "off" disallows queries during recovery
763c763
< #max_locks_per_transaction = 64               # min 10
---
> max_locks_per_transaction = 32                # min 10
```

10. update `max_wal_senders` and `max_locks_per_transaction` based on replica error logs
