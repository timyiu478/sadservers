## "Zaragoza": Test changing critical files

### Problem

Description: The goal is to make the script /home/admin/check.sh return OK, without editing the original /etc/hosts file.

Think testing changes in the critical directory /etc in a safe way. In tnis case, adding "127.0.0.1 my.local.test" to /etc/hosts .

There would be many ways of trying to do this with "sudo" access, like the usual procedure of making a copy of the config file, editing there and copying or renaming back to the original file. In our case, to avoid all those simple solutions, there is no general "sudo" privileges in this scenario.

https://sadservers.com/scenario/zaragoza

### Solution

### 1. Try to unshare approach

```bash
admin@i-083d7a323fb6560e7:~/unionfs-fuse-3.6$ unshare -r -m bash
root@i-083d7a323fb6560e7:~/unionfs-fuse-3.6# ls
CMakeLists.txt  LICENSE   NEWS       examples       man            src   test_all.py     test_vagrant_macos.sh
CREDITS         Makefile  README.md  macos_vagrant  mount.unionfs  test  test_legacy.sh  test_vagrant_ubuntu.sh
root@i-083d7a323fb6560e7:~/unionfs-fuse-3.6# cd ~
root@i-083d7a323fb6560e7:~# cp /etc/hosts hosts
root@i-083d7a323fb6560e7:~# vim hosts 
root@i-083d7a323fb6560e7:~# mount --bind ./hosts /etc/hosts
root@i-083d7a323fb6560e7:~# cat /etc/hosts
# Your system has configured 'manage_etc_hosts' as True.
# As a result, if you wish for changes to this file to persist
# then you will need to either
# a.) make changes to the master file in /etc/cloud/templates/hosts.debian.tmpl
# b.) change or remove the value of 'manage_etc_hosts' in
#     /etc/cloud/cloud.cfg or cloud-config from user-data
#
127.0.1.1 i-083d7a323fb6560e7.us-east-2.compute.internal i-083d7a323fb6560e7
127.0.0.1 localhost
127.0.0.1 my.local.test

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhostsadmin@i-083d7a323fb6560e7:~/unionfs-fuse-3.6$ unshare -r -m bash
root@i-083d7a323fb6560e7:~/unionfs-fuse-3.6# ls
CMakeLists.txt  LICENSE   NEWS       examples       man            src   test_all.py     test_vagrant_macos.sh
CREDITS         Makefile  README.md  macos_vagrant  mount.unionfs  test  test_legacy.sh  test_vagrant_ubuntu.sh
root@i-083d7a323fb6560e7:~/unionfs-fuse-3.6# cd ~
root@i-083d7a323fb6560e7:~# cp /etc/hosts hosts
root@i-083d7a323fb6560e7:~# vim hosts 
root@i-083d7a323fb6560e7:~# mount --bind ./hosts /etc/hosts
root@i-083d7a323fb6560e7:~# cat /etc/hosts
# Your system has configured 'manage_etc_hosts' as True.
# As a result, if you wish for changes to this file to persist
# then you will need to either
# a.) make changes to the master file in /etc/cloud/templates/hosts.debian.tmpl
# b.) change or remove the value of 'manage_etc_hosts' in
#     /etc/cloud/cloud.cfg or cloud-config from user-data
#
127.0.1.1 i-083d7a323fb6560e7.us-east-2.compute.internal i-083d7a323fb6560e7
127.0.0.1 localhost
127.0.0.1 my.local.test

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
```
