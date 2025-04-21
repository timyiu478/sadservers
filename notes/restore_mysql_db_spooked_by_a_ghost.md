## "Abaokoro": Restore MySQL Databases Spooked by a Ghost

### Problem

There are three databases that need to be restored. You need to create three databases called "first", "second" and "third" and restore the databases using the file "/home/admin/dbs_to_restore.zip".

If you encounter an issue while restoring the database, fix it.

Ref: https://sadservers.com/scenario/abaokoro

### Solution

1. try to unzip to get the sqls for restoring

```
admin@i-0fecf4fee86a95e45:~$ tar -xf dbs_to_restore.tar.gz 
tar: first.sql: Cannot write: Disk quota exceeded
tar: second.sql: Cannot write: Disk quota exceeded
tar: third.sql: Cannot write: Disk quota exceeded
tar: Exiting with failure status due to previous errors
```

2. check file system disk usage

```
admin@i-0fecf4fee86a95e45:~$ df
Filesystem      1K-blocks    Used Available Use% Mounted on
udev               222712       0    222712   0% /dev
tmpfs               46652     408     46244   1% /run
/dev/nvme0n1p1    8025124 7461128    134788  99% /
```

3. check what files used most disk space

5.0G    /var/log/custom

```
admin@i-0fecf4fee86a95e45:~$ sudo du -h / | sort -rh | head -n 10
du: cannot access '/proc/1255/task/1255/fd/4': No such file or directory
du: cannot access '/proc/1255/task/1255/fdinfo/4': No such file or directory
du: cannot access '/proc/1255/fd/3': No such file or directory
du: cannot access '/proc/1255/fdinfo/3': No such file or directory
7.2G    /
5.6G    /var
5.1G    /var/log
5.0G    /var/log/custom
1.5G    /usr
479M    /usr/lib
468M    /usr/bin
280M    /usr/share
267M    /var/lib
261M    /var/cache
```

4. remove all logs inside `/var/log/custom/`

```
admin@i-0fecf4fee86a95e45:/var/log/custom$ df
Filesystem      1K-blocks    Used Available Use% Mounted on
udev               222712       0    222712   0% /dev
tmpfs               46652     408     46244   1% /run
/dev/nvme0n1p1    8025124 2229316   5366600  30% /
```

5. there should be some process keep generate such big size log file

```
admin@i-0fecf4fee86a95e45:~$ sudo du -h / | sort -rh | head -n 10
du: cannot access '/proc/1643/task/1643/fd/4': No such file or directory
du: cannot access '/proc/1643/task/1643/fdinfo/4': No such file or directory
du: cannot access '/proc/1643/fd/3': No such file or directory
du: cannot access '/proc/1643/fdinfo/3': No such file or directory
7.2G    /
5.6G    /var
5.1G    /var/log
5.0G    /var/log/custom
admin@i-0fecf4fee86a95e45:/var/log/custom$ ls -alt
total 5231844
-rw-r--r--  1 admin admin          0 Apr 21 18:36 2025-02-02.log
drwxr-xr-x  2 admin root        4096 Apr 21 18:36 .
-rw-r--r--  1 admin admin          0 Apr 21 18:35 2024-11-17.log
-rw-r--r--  1 admin admin          0 Apr 21 18:35 2024-06-07.log
-rw-r--r--  1 admin admin          0 Apr 21 18:35 2024-06-25.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2025-04-19.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2024-08-20.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2025-01-16.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2024-04-23.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2025-01-31.log
-rw-r--r--  1 admin admin          0 Apr 21 18:34 2024-05-22.log
-rw-r--r--  1 admin admin 5357395968 Apr 21 18:34 2025-03-09.log
```

6. delete the logs again and change `/var/log/custom/` to read only

```
admin@i-0fecf4fee86a95e45:/var/log$ ls -alt | grep custom
dr--------   2 admin   root              4096 Apr 21 18:43 custom
```

7. unzip `dbs_to_restore.tar.gz`

```
admin@i-0fecf4fee86a95e45:~$ tar -xf dbs_to_restore.tar.gz 
admin@i-0fecf4fee86a95e45:~$ ls -alt
total 159812
drwxr-xr-x 5 admin admin     4096 Apr 21 18:45 .
-rw-r--r-- 1 root  root         0 Apr 21 18:26 .bash_history
drwx------ 2 admin admin     4096 Mar 24  2024 .ssh
drwxrwxrwx 2 admin admin     4096 Mar 24  2024 agent
-rw-r--r-- 1 root  root  33594915 Feb 22  2024 dbs_to_restore.tar.gz
-rw-r--r-- 1 admin admin 43336368 Feb 22  2024 third.sql
-rw-r--r-- 1 admin admin 43336369 Feb 22  2024 second.sql
-rw-r--r-- 1 admin admin 43336368 Feb 22  2024 first.sql
drwx------ 3 admin admin     4096 Feb 17  2024 .ansible
drwxr-xr-x 3 root  root      4096 Feb 17  2024 ..
-rw-r--r-- 1 admin admin      220 Mar 27  2022 .bash_logout
-rw-r--r-- 1 admin admin     3526 Mar 27  2022 .bashrc
-rw-r--r-- 1 admin admin      807 Mar 27  2022 .profile
```

8. check if databases first, second, and third exist

Nope.

```
MariaDB [(none)]> SHOW DATABASEs;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
3 rows in set (0.019 sec)
```

9. Create databases first, second, and third

```
MariaDB [(none)]> CREATE DATABASE first;
Query OK, 1 row affected (0.001 sec)

MariaDB [(none)]> CREATE DATABASE second;
Query OK, 1 row affected (0.000 sec)

MariaDB [(none)]> CREATE DATABASE third;
Query OK, 1 row affected (0.000 sec)

MariaDB [(none)]> SHOW DATABASEs;
+--------------------+
| Database           |
+--------------------+
| first              |
| information_schema |
| mysql              |
| performance_schema |
| second             |
| third              |
+--------------------+
6 rows in set (0.000 sec)
```

10. restore databases

```
admin@i-0fecf4fee86a95e45:~$ sudo mysql -u root first < first.sql 
admin@i-0fecf4fee86a95e45:~$ sudo mysql -u root second < second.sql 
admin@i-0fecf4fee86a95e45:~$ sudo mysql -u root third < third.sql
```
