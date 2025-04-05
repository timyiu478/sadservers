## "Bern": Docker web container can't connect to db container.

### Problem

https://sadservers.com/newserver/bern

### Solution

1. check wordpress database connection configs

```
admin@i-013d975acfb4181d6:~/html$ cat wp-config.php | grep WORDPRESS_DB
define( 'DB_NAME', getenv_docker('WORDPRESS_DB_NAME', 'wordpress') );
define( 'DB_USER', getenv_docker('WORDPRESS_DB_USER', 'example username') );
define( 'DB_PASSWORD', getenv_docker('WORDPRESS_DB_PASSWORD', 'example password') );
define( 'DB_HOST', getenv_docker('WORDPRESS_DB_HOST', 'mysql') );
define( 'DB_CHARSET', getenv_docker('WORDPRESS_DB_CHARSET', 'utf8') );
define( 'DB_COLLATE', getenv_docker('WORDPRESS_DB_COLLATE', '') );
```

2. get DB name and password from DB container

```
admin@i-013d975acfb4181d6:/$ sudo docker exec -it 0eef97284c44 /bin/bash
root@0eef97284c44:/# printenv | grep MYSQL
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=wordpress
```

3. check the DB configs from web server container

The password should be correct.

```
root@6ffb084b515c:/var/www/html# printenv | grep WORDPRESS_DB
WORDPRESS_DB_PASSWORD=password
WORDPRESS_DB_USER=root
```

4. check the docker network setting

- 2 containers are connected via the bridge.
- DB ip = 172.17.0.2


```
admin@i-013d975acfb4181d6:~$ sudo docker network ls
NETWORK ID     NAME      DRIVER    SCOPE
a4ded637bec8   bridge    bridge    local
d8958b2ba55c   host      host      local
a40cd0d67e94   none      null      local
admin@i-013d975acfb4181d6:~$ sudo docker network inspect a4ded637bec8
[
    {
        "Name": "bridge",
        "Id": "a4ded637bec8243672d167e6851f69a57afb022d1421d4f7517591c05fa2854a",
        "Created": "2025-04-05T08:28:14.678729862Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.17.0.0/16",
                    "Gateway": "172.17.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "0eef97284c44a702a82c97921983d398e6268dfbb9db242b622598d2d863ccdf": {
                "Name": "mariadb",
                "EndpointID": "b18734e6ef44994fa594ae5e03a39844fb340aae0625167b4781b7b9be771b80",
                "MacAddress": "02:42:ac:11:00:02",
                "IPv4Address": "172.17.0.2/16",
                "IPv6Address": ""
            },
            "6ffb084b515ca482ac58fad406b10837b44fb55610acbb35b8ed4a0fb24de50c": {
                "Name": "wordpress",
                "EndpointID": "7bd72f76ef06a0865184c01a6fc3548c298c5d74b563fa7d04ca39b57bfb9dcf",
                "MacAddress": "02:42:ac:11:00:03",
                "IPv4Address": "172.17.0.3/16",
                "IPv6Address": ""
            }
        },
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]
admin@i-013d975acfb4181d6:~$ sudo docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED       STATUS          PORTS                    NAMES
6ffb084b515c   wordpress:sad    "docker-entrypoint.s…"   2 years ago   Up 25 minutes   0.0.0.0:80->80/tcp       wordpress
0eef97284c44   mariadb:latest   "docker-entrypoint.s…"   2 years ago   Up 25 minutes   0.0.0.0:3306->3306/tcp   mariadb
```

5. try `mysqladmin -h 172.17.0.2 -u root -ppassword ping`

```
root@6ffb084b515c:/var/www/html# mysqladmin -h 172.17.0.2 -u root -ppassword ping
mysqladmin: connect to server at '172.17.0.2' failed
error: 'Access denied for user 'root'@'172.17.0.3' (using password: YES)'
```

6. login DB in DB container

```
root@0eef97284c44:~# mysql -ppassword wordpress
```

7. check user and user permissions

root user in any host should have sufficient permissions.

```
MariaDB [wordpress]> SHOW GRANTS FOR 'root'@'%';
+--------------------------------------------------------------------------------------------------------------------------------+
| Grants for root@%                                                                                                              |
+--------------------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO `root`@`%` IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' WITH GRANT OPTION |
+--------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.000 sec)

MariaDB [wordpress]> SELECT host, user, password FROM mysql.user;
+-----------+-------------+-------------------------------------------+
| Host      | User        | Password                                  |
+-----------+-------------+-------------------------------------------+
| localhost | mariadb.sys |                                           |
| localhost | root        | *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19 |
| %         | root        | *2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19 |
+-----------+-------------+-------------------------------------------+
3 rows in set (0.001 sec)

MariaDB [wordpress]> SHOW GRANTS FOR 'root'@'%';
+--------------------------------------------------------------------------------------------------------------------------------+
| Grants for root@%                                                                                                              |
+--------------------------------------------------------------------------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO `root`@`%` IDENTIFIED BY PASSWORD '*2470C0C06DEE42FD1618BB99005ADCA2EC9D1E19' WITH GRANT OPTION |
+--------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.000 sec)
```

8. try `mysqladmin -h 172.17.0.2 -u root -ppassword ping` again after restarting the VM

It works this time.

```
admin@i-088d50db3f30e797b:/$ sudo docker exec -it wordpress /bin/bash
root@6ffb084b515c:/var/www/html# mysqladmin -h 172.17.0.2 -u root -ppassword ping
mysqld is alive
```

9. check web server container's `/etc/hosts`

`mysql` is not in there.

```
admin@i-02981813a22a1542e:/$ cat /var/lib/docker/containers/6ffb084b515ca482ac58fad406b10837b44fb55610acbb35b8ed4a0fb24de50c/hosts 
cat: /var/lib/docker/containers/6ffb084b515ca482ac58fad406b10837b44fb55610acbb35b8ed4a0fb24de50c/hosts: Permission denied
admin@i-02981813a22a1542e:/$ sudo cat /var/lib/docker/containers/6ffb084b515ca482ac58fad406b10837b44fb55610acbb35b8ed4a0fb24de50c/hosts 
127.0.0.1       localhost
::1     localhost ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
172.17.0.3      6ffb084b515c mysql
```

10. add `mysql` in `/etc/hosts` of web server container  

```
admin@i-0942ab0f87e50e36a:/$ sudo docker run --name wordpress --add-host=mysql:172.17.0.2  -p 80:80 -d wordpress:sad
841cb4a38ebd39db40510ceba8f2b21e7d5f29dd232a270c26b9eab68fde7443
admin@i-0942ab0f87e50e36a:/$ sudo docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED         STATUS          PORTS                    NAMES
841cb4a38ebd   wordpress:sad    "docker-entrypoint.s…"   5 seconds ago   Up 4 seconds    0.0.0.0:80->80/tcp       wordpress
0eef97284c44   mariadb:latest   "docker-entrypoint.s…"   2 years ago     Up 10 minutes   0.0.0.0:3306->3306/tcp   mariadb
admin@i-0942ab0f87e50e36a:/$ sudo docker exec wordpress mysqladmin -h mysql -u root -ppassword ping
mysqld is alive
```
