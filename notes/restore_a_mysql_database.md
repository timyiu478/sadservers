## "Rosario": Restore a MySQL database

### Problem

A developer created a database named 'main' but now some data is missing in the database. You need to restore the database using the the dump "/home/admin/backup.sql".

The issue is that the developer forgot the root password for the MariaDB server.

If you encounter an issue while restoring the database, fix it.

https://sadservers.com/scenario/rosario

### Solution

1. check the status of `mysql`


- Access denied for user 'root'@'localhost' (using password: NO)
- Reading datadir from the MariaDB server failed.
- User: root

```
admin@i-0615ed5cbee8dcb00:~$ systemctl status mysql
● mariadb.service - MariaDB 10.5.23 database server
     Loaded: loaded (/lib/systemd/system/mariadb.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-04-21 07:56:23 UTC; 1min 14s ago
       Docs: man:mariadbd(8)
             https://mariadb.com/kb/en/library/systemd/
   Main PID: 684 (mariadbd)
     Status: "Taking your SQL requests now..."
      Tasks: 9 (limit: 521)
     Memory: 67.3M
        CPU: 232ms
     CGroup: /system.slice/mariadb.service
             └─684 /usr/sbin/mariadbd

Apr 21 07:56:23 i-0615ed5cbee8dcb00 systemd[1]: Started MariaDB 10.5.23 database server.
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[716]: Upgrading MySQL tables if necessary.
Apr 21 07:56:23 i-0615ed5cbee8dcb00 mariadbd[684]: 2025-04-21  7:56:23 3 [Warning] Access denied for user 'root'@'localhost' (using password: NO)
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[719]: Looking for 'mariadb' as: /usr/bin/mariadb
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[719]: Reading datadir from the MariaDB server failed. Got the following error when execut>
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[719]: ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[719]: FATAL ERROR: Upgrade failed
Apr 21 07:56:23 i-0615ed5cbee8dcb00 /etc/mysql/debian-start[731]: Checking for insecure root accounts.
Apr 21 07:56:23 i-0615ed5cbee8dcb00 mariadbd[684]: 2025-04-21  7:56:23 4 [Warning] Access denied for user 'root'@'localhost' (using password: NO)
Apr 21 07:56:23 i-0615ed5cbee8dcb00 debian-start[735]: ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)
```

2. allow root access by skipping grant tables

```
admin@i-0615ed5cbee8dcb00:/etc/mysql$ cat mariadb.cnf
[mysqld]
skip-grant-tables
```

3. check if `main` database exists

```
MariaDB [(none)]> \u main
Database changed
MariaDB [main]> show tables;
Empty set (0.000 sec)
```

4. try to restore the `main` database using `backup.sql`

```
admin@i-0385556d8ea7cc61d:~$ sudo mysql -u root main < backup.sql 
ERROR 1064 (42000) at line 7: You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near '?
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */?
/*!4010...' at line 1
```

5. compare the running database verion and the database version that dump `backup.sql`

Server version:         10.5.23-MariaDB-0+deb11u1 Debian 11

vs

-- Server version       10.5.21-MariaDB-0+deb11u1

```
MariaDB [(none)]> status
--------------
mysql  Ver 15.1 Distrib 10.5.23-MariaDB, for debian-linux-gnu (x86_64) using  EditLine wrapper

Connection id:          31
Current database:
Current user:           root@
SSL:                    Not in use
Current pager:          stdout
Using outfile:          ''
Using delimiter:        ;
Server:                 MariaDB
Server version:         10.5.23-MariaDB-0+deb11u1 Debian 11

admin@i-0385556d8ea7cc61d:~$ cat backup.sql 
-- MariaDB dump 10.19  Distrib 10.5.21-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: main
-- ------------------------------------------------------
-- Server version       10.5.21-MariaDB-0+deb11u1
```

6. replace `?` to `;` to fix syntax error

```
admin@i-0385556d8ea7cc61d:~$ sed -i 's/\?$/;/g' backup.sql
```

7. try to restore `main` database

```
admin@i-0385556d8ea7cc61d:~$ sudo mysql -u root main < backup.sql
admin@i-0385556d8ea7cc61d:~$ sudo mysql -u root main
MariaDB [main]> show tables
    -> ;
+----------------+
| Tables_in_main |
+----------------+
| solution       |
+----------------+
1 row in set (0.000 sec)

MariaDB [main]> select * from solution;
```


