## "Zaragoza": Test changing critical files

### Problem

Description: The goal is to make the script /home/admin/check.sh return OK, without editing the original /etc/hosts file.

Think testing changes in the critical directory /etc in a safe way. In tnis case, adding "127.0.0.1 my.local.test" to /etc/hosts .

There would be many ways of trying to do this with "sudo" access, like the usual procedure of making a copy of the config file, editing there and copying or renaming back to the original file. In our case, to avoid all those simple solutions, there is no general "sudo" privileges in this scenario.

Source: https://sadservers.com/scenario/zaragoza

### Solution

1. Copy `/etc/hosts` to `~/hosts`

2. Add an new entry `127.0.0.1 my.local.test` to `~/hosts`

3. `mount --bind hosts /etc/hosts`

```bash
admin@i-0ae37f6120f883226:~$ sudo mount --bind hosts /etc/hosts
admin@i-0ae37f6120f883226:~$ cat /etc/hosts
# Your system has configured 'manage_etc_hosts' as True.
# As a result, if you wish for changes to this file to persist
# then you will need to either
# a.) make changes to the master file in /etc/cloud/templates/hosts.debian.tmpl
# b.) change or remove the value of 'manage_etc_hosts' in
#     /etc/cloud/cloud.cfg or cloud-config from user-data
#
127.0.1.1 i-0ae37f6120f883226.us-east-2.compute.internal i-0ae37f6120f883226
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

### Notes

#### Bind mount operation

Remount part of the file hierarchy somewhere else. The call is:

    mount --bind olddir newdir

or by using this fstab entry:

    /olddir /newdir none bind

After this call the same contents are accessible in two places.

It is important to understand that "bind" does not create any
second-class or special node in the kernel VFS. The "bind" is just
another operation to attach a filesystem. There is nowhere stored
information that the filesystem has been attached by a "bind"
operation. The olddir and newdir are independent and the olddir
may be unmounted.

One can also remount a single file (on a single file). It’s also
possible to use a bind mount to create a mountpoint from a regular
directory, for example:

    mount --bind foo foo

The bind mount call attaches only (part of) a single filesystem,
not possible submounts. The entire file hierarchy including
submounts can be attached a second place by using:

    mount --rbind olddir newdir

Note that the filesystem mount options maintained by the kernel
will remain the same as those on the original mount point. The
userspace mount options (e.g., _netdev) will not be copied by
mount and it’s necessary to explicitly specify the options on the
mount command line.

Ref: https://man7.org/linux/man-pages/man8/mount.8.html
