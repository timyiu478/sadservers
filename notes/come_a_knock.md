## "Taipei": Come a-knocking

### Problem

https://sadservers.com/newserver/taipei

### Solution

1. use `nmap` to check open ports

```
admin@i-0fb926b622663f965:~$ nmap localhost -p-
Starting Nmap 7.80 ( https://nmap.org ) at 2025-03-28 14:19 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000068s latency).
Not shown: 65532 closed ports
PORT     STATE SERVICE
22/tcp   open  ssh
6767/tcp open  bmc-perf-agent
8080/tcp open  http-proxy
```

2. `knock` a server

```
Nmap done: 1 IP address (1 host up) scanned in 1.04 seconds
admin@i-0fb926b622663f965:~$ knock localhost 6767 | curl localhost
Who is there?admin@i-0fb926b622663f965:~$ 
```
