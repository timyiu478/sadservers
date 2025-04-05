## "Jakarta": it's always DNS.

### Problem

Can't ping `google.com`. It returns `ping: google.com: Name or service not known`. Expected is being able to resolve the hostname. (Note: currently the VMs can't ping outside so there's no automated check for the solution).

https://sadservers.com/scenario/jakarta

### Solution

1. check `/etc/resolv.conf`

```
ubuntu@i-0b8e1e10503750822:/$ cat /etc/resolv.conf 
# This is /run/systemd/resolve/stub-resolv.conf managed by man:systemd-resolved(8).
# Do not edit.
#
# This file might be symlinked as /etc/resolv.conf. If you're looking at
# /etc/resolv.conf and seeing this text, you have followed the symlink.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "resolvectl status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs should typically not access this file directly, but only
# through the symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a
# different way, replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.

nameserver 127.0.0.53
options edns0 trust-ad
search us-east-2.compute.internal
```

2. check the status of `systemd-resolved`

```
ubuntu@i-0b8e1e10503750822:/$ resolvectl status
Global
       Protocols: -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
resolv.conf mode: stub

Link 2 (ens5)
Current Scopes: DNS
     Protocols: +DefaultRoute +LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
   DNS Servers: 10.0.0.2
    DNS Domain: us-east-2.compute.internal
```

3. try `dig google.com`

It works.

```
ubuntu@i-0b8e1e10503750822:/$ dig google.com

; <<>> DiG 9.18.1-1ubuntu1.1-Ubuntu <<>> google.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 64850
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;google.com.                    IN      A

;; ANSWER SECTION:
google.com.             3       IN      A       142.250.191.174

;; Query time: 4 msec
;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)
;; WHEN: Sat Apr 05 07:16:22 UTC 2025
;; MSG SIZE  rcvd: 55
```

4. try `ping 142.250.191.174`

It works.

```
ubuntu@i-0b8e1e10503750822:/$ ping 142.250.191.174
PING 142.250.191.174 (142.250.191.174) 56(84) bytes of data.
64 bytes from 142.250.191.174: icmp_seq=1 ttl=58 time=7.97 ms
64 bytes from 142.250.191.174: icmp_seq=2 ttl=58 time=7.98 ms
^C
--- 142.250.191.174 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 7.974/7.978/7.983/0.004 ms
```

5. the difference between `ping` and `dig` on resolving domain name

- `dig` calls the DNS server directly configured in `127.0.0.53`.
- `ping`: follows the `nsswitch.conf` that defines the order of name resolution mechanisms on the system
    - `hosts: files dns`
        - `files`: instructs the system to check `/etc/hosts` first.
        - `dns`: tells the system to query DNS servers if no match is found in `/etc/hosts`

6. check `nsswitch.conf`

It only check `files`.

```
ubuntu@i-0b8e1e10503750822:/$ cat /etc/nsswitch.conf 
# /etc/nsswitch.conf
#
# Example configuration of GNU Name Service Switch functionality.
# If you have the `glibc-doc-reference' and `info' packages installed, try:
# `info libc "Name Service Switch"' for information about this file.

passwd:         files systemd
group:          files systemd
shadow:         files
gshadow:        files

hosts:          files
networks:       files

protocols:      db files
services:       db files
ethers:         db files
rpc:            db files

netgroup:       nis
```

7. add `dns` back to `hosts:          files` in `/etc/nsswitch.conf`

8. try to `ping google.com`

```
ubuntu@i-0b8e1e10503750822:/$ ping google.com
PING google.com (142.250.190.14) 56(84) bytes of data.
64 bytes from ord37s32-in-f14.1e100.net (142.250.190.14): icmp_seq=1 ttl=58 time=8.06 ms
64 bytes from ord37s32-in-f14.1e100.net (142.250.190.14): icmp_seq=2 ttl=58 time=8.07 ms
^C
--- google.com ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 8.061/8.063/8.065/0.002 ms
```
