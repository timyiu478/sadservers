## "Lisbon": etcd SSL cert troubles

### Problem

> There's an etcd server running on https://localhost:2379 , get the value for the key "foo", ie etcdctl get foo or curl https://localhost:2379/v2/keys/foo

https://sadservers.com/scenario/lisbon

### Solution

1. try to get the value of key `foo`

```
admin@i-007917f26b19642e3:/$ etcdctl get foo
Error:  client: etcd cluster is unavailable or misconfigured; error #0: x509: certificate has expired or is not yet valid: current time 2026-03-31T08:50:42Z is after 2023-01-30T00:02:48Z

error #0: x509: certificate has expired or is not yet valid: current time 2026-03-31T08:50:42Z is after 2023-01-30T00:02:48Z
```

2. change date before `2023-01-30T00:02:48Z`

```
admin@i-0f019ab704f87f554:/$ sudo date -s "28 JAN 2023 18:00:00"
Sat Jan 28 18:00:00 UTC 2023
admin@i-0f019ab704f87f554:/$ date
Sat Jan 28 18:00:05 UTC 2023
admin@i-0f019ab704f87f554:/$ etcdctl get foo
Error:  client: response is invalid json. The endpoint is probably not valid etcd cluster endpoint.
```

3. try to use curl

there is an nginx server running

```
admin@i-0f019ab704f87f554:/$ curl https://localhost:2379/v2/keys/foo
<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.18.0</center>
</body>
</html>
```

4. tried to play with nginx but no help

there is no setting that integrate nginx with etcd

5. tried to look at iptables (filter table) and see nothing

6. the hint tells us to look at iptable (**nat** table)

any tcp port 2379 redirets to 443

```
admin@i-0cc39c1f05ce6b8f1:/$ sudo iptables -t nat -L
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination         
DOCKER     all  --  anywhere             anywhere             ADDRTYPE match dst-type LOCAL

Chain INPUT (policy ACCEPT)
target     prot opt source               destination         

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination         
REDIRECT   tcp  --  anywhere             anywhere             tcp dpt:2379 redir ports 443
DOCKER     all  --  anywhere            !127.0.0.0/8          ADDRTYPE match dst-type LOCAL

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination         
MASQUERADE  all  --  172.17.0.0/16        anywhere            

Chain DOCKER (2 references)
target     prot opt source               destination         
RETURN     all  --  anywhere             anywhere
```

7. remove the tcp port redirection

```
admin@i-0cc39c1f05ce6b8f1:/$ sudo iptables -t nat -D OUTPUT 1
```

### Lessions Learnt

- dont just look the default table of iptables
- can observe network packet patterns when no cue with SSL issue
