## "Kihei": Surely Not Another Disk Space Scenario

### Problem

> There is a /home/admin/kihei program. Make the changes necessary so it runs succesfully, without deleting the /home/admin/datafile file.

https://sadservers.com/scenario/kihei

### Solution

1. try to run `./kihei`

```
admin@i-09e85c8bc64a76548:~$ ./kihei 
panic: exit status 1

goroutine 1 [running]:
main.main()
        ./main.go:64 +0x47d
```

2. check the disk usage of `/home/admin` directory

```
admin@i-09e85c8bc64a76548:~$ df -h ~
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p1  7.7G  6.2G  1.1G  85% /
admin@i-09e85c8bc64a76548:~$ ls -alt
total 5245084
drwxr-xr-x 2 admin root        4096 Mar 31 13:46 data
drwxr-xr-x 7 admin admin       4096 Mar 31 13:46 .
-rw------- 1 admin admin        688 Mar 31 13:46 .viminfo
drwxr-xr-x 3 admin admin       4096 Mar 31 13:45 .config
-rw-r--r-- 1 root  root           0 Mar 31 13:45 .bash_history
drwxr-xr-x 2 admin root        4096 Sep 17  2023 agent
-rwxr-xr-x 1 admin root     2207109 Sep 17  2023 kihei
-rw-r--r-- 1 root  root  5368709120 Sep 17  2023 datafile
drwx------ 3 admin admin       4096 Sep 17  2023 .ansible
drwx------ 2 admin admin       4096 Sep 17  2023 .ssh
drwxr-xr-x 3 root  root        4096 Sep 17  2023 ..
-rw-r--r-- 1 admin admin        220 Aug  4  2021 .bash_logout
-rw-r--r-- 1 admin admin       3526 Aug  4  2021 .bashrc
-rw-r--r-- 1 admin admin        807 Aug  4  2021 .profile
```

3. tried to remove `datafile` and run `./kihei`

it works.

```
admin@i-09e85c8bc64a76548:~$ ./kihei 
Done.
```

4. try to free up some space

```
admin@i-04c05506a9523647b:/$ ls -alt
total 68
drwxrwxrwt   9 root root  4096 Mar 31 14:20 tmp
drwxr-xr-x  73 root root  4096 Mar 31 14:18 etc
drwxr-xr-x  18 root root  4096 Mar 31 14:18 .
drwxr-xr-x  18 root root  4096 Mar 31 14:18 ..
drwxr-xr-x  23 root root   700 Mar 31 14:18 run
drwxr-xr-x  13 root root  2960 Mar 31 14:18 dev
dr-xr-xr-x 141 root root     0 Mar 31 14:18 proc
dr-xr-xr-x  13 root root     0 Mar 31 14:18 sys
drwxr-xr-x   4 root root  4096 Sep 17  2023 boot
drwx------   3 root root  4096 Sep 17  2023 root
drwxr-xr-x   3 root root  4096 Sep 17  2023 home
drwxr-xr-x  14 root root  4096 Sep 28  2021 usr
drwxr-xr-x  11 root root  4096 Sep 28  2021 var
drwxr-xr-x   2 root root  4096 Sep 28  2021 media
drwxr-xr-x   2 root root  4096 Sep 28  2021 opt
drwxr-xr-x   2 root root  4096 Sep 28  2021 srv
drwxr-xr-x   2 root root  4096 Sep 28  2021 mnt
lrwxrwxrwx   1 root root    10 Sep 28  2021 libx32 -> usr/libx32
lrwxrwxrwx   1 root root     9 Sep 28  2021 lib32 -> usr/lib32
lrwxrwxrwx   1 root root     9 Sep 28  2021 lib64 -> usr/lib64
lrwxrwxrwx   1 root root     7 Sep 28  2021 lib -> usr/lib
lrwxrwxrwx   1 root root     8 Sep 28  2021 sbin -> usr/sbin
lrwxrwxrwx   1 root root     7 Sep 28  2021 bin -> usr/bin
drwx------   2 root root 16384 Sep 28  2021 lost+found
```

5. remove `lost_foun` and then try to rerun the program

Same error

```
admin@i-04c05506a9523647b:/$ sudo rm -rf lost+found
```

6. check the memory usage

```
admin@i-04c05506a9523647b:~$ vmstat -s
       466340 K total memory
       101168 K used memory
       122308 K active memory
       232284 K inactive memory
        11324 K free memory
        28784 K buffer memory
       325064 K swap cache
            0 K total swap
            0 K used swap
            0 K free swap
          841 non-nice user cpu ticks
            5 nice user cpu ticks
          789 system cpu ticks
       233642 idle cpu ticks
          773 IO-wait cpu ticks
            0 IRQ cpu ticks
            5 softirq cpu ticks
          113 stolen cpu ticks
       230999 pages paged in
       212045 pages paged out
            0 pages swapped in
            0 pages swapped out
       276913 interrupts
       461815 CPU context switches
   1743430725 boot time
         1434 forks
```

7. check datafile permission is not the cause of `kihei` failure

```
admin@i-04c05506a9523647b:~$ sudo chmod 777 datafile
admin@i-04c05506a9523647b:~$ ./kihei 
panic: exit status 1

goroutine 1 [running]:
main.main()
        ./main.go:64 +0x47d
```

8. try to reduce the datafile size

it works.

```
admin@i-05cccd0e68ed9feca:~$ ls -alt
total 2200
drwxr-xr-x 7 admin admin    4096 Mar 31 15:35 .
-rw-r--r-- 1 root  root     1019 Mar 31 15:35 datafile
drwxr-xr-x 3 admin admin    4096 Mar 31 15:28 .config
-rw-r--r-- 1 root  root        0 Mar 31 15:26 .bash_history
drwxr-xr-x 2 admin root     4096 Sep 17  2023 agent
-rwxr-xr-x 1 admin root  2207109 Sep 17  2023 kihei
drwxr-xr-x 2 admin root     4096 Sep 17  2023 data
drwx------ 3 admin admin    4096 Sep 17  2023 .ansible
drwx------ 2 admin admin    4096 Sep 17  2023 .ssh
drwxr-xr-x 3 root  root     4096 Sep 17  2023 ..
-rw-r--r-- 1 admin admin     220 Aug  4  2021 .bash_logout
-rw-r--r-- 1 admin admin    3526 Aug  4  2021 .bashrc
-rw-r--r-- 1 admin admin     807 Aug  4  2021 .profile
admin@i-05cccd0e68ed9feca:~$ ./kihei 
Done.
```

9. strace the program

key line:

```
newfstatat(AT_FDCWD, "/home/admin/data/newdatafile", {st_mode=S_IFREG|0644, st_size=1500000000, ...}, 0) = 0
```

full trace:

```
admin@i-05cccd0e68ed9feca:~$ strace ./kihei 
execve("./kihei", ["./kihei"], 0x7ffc6b9a4700 /* 14 vars */) = 0
arch_prctl(ARCH_SET_FS, 0x56b030)       = 0
sched_getaffinity(0, 8192, [0, 1])      = 8
openat(AT_FDCWD, "/sys/kernel/mm/transparent_hugepage/hpage_pmd_size", O_RDONLY) = 3
read(3, "2097152\n", 20)                = 8
close(3)                                = 0
mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b87a0c000
mmap(NULL, 131072, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b879ec000
mmap(NULL, 1048576, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b878ec000
mmap(NULL, 8388608, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b870ec000
mmap(NULL, 67108864, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b830ec000
mmap(NULL, 536870912, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b630ec000
mmap(0xc000000000, 67108864, PROT_NONE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0xc000000000
mmap(NULL, 33554432, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b610ec000
mmap(NULL, 2165776, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b60edb000
mmap(0xc000000000, 4194304, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0xc000000000
mmap(0x7f2b879ec000, 131072, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f2b879ec000
mmap(0x7f2b8796c000, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f2b8796c000
mmap(0x7f2b874f2000, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f2b874f2000
mmap(0x7f2b8511c000, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f2b8511c000
mmap(0x7f2b7326c000, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f2b7326c000
mmap(NULL, 1048576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b60ddb000
mmap(NULL, 65536, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b60dcb000
mmap(NULL, 65536, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b60dbb000
rt_sigprocmask(SIG_SETMASK, NULL, [], 8) = 0
sigaltstack(NULL, {ss_sp=NULL, ss_flags=SS_DISABLE, ss_size=0}) = 0
sigaltstack({ss_sp=0xc000004000, ss_flags=0, ss_size=32768}, NULL) = 0
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
gettid()                                = 1231
rt_sigaction(SIGHUP, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGHUP, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGINT, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGINT, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGQUIT, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGQUIT, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGILL, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGILL, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGTRAP, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGTRAP, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGABRT, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGABRT, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGBUS, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGBUS, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGFPE, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGFPE, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGUSR1, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGUSR1, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGSEGV, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGSEGV, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGUSR2, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGUSR2, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGPIPE, NULL, {sa_handler=SIG_IGN, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGPIPE, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGALRM, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGALRM, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGTERM, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGTERM, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGSTKFLT, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGSTKFLT, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGCHLD, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGCHLD, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGURG, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGURG, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGXCPU, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGXCPU, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGXFSZ, NULL, {sa_handler=SIG_IGN, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGXFSZ, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGVTALRM, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGVTALRM, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGPROF, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGPROF, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGWINCH, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGWINCH, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGIO, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGIO, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGPWR, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGPWR, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGSYS, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGSYS, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRTMIN, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_1, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_1, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_2, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_3, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_3, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_4, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_4, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_5, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_5, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_6, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_6, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_7, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_7, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_8, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_8, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_9, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_9, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_10, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_10, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_11, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_11, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_12, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_12, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_13, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_13, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_14, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_14, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_15, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_15, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_16, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_16, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_17, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_17, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_18, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_18, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_19, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_19, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_20, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_20, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_21, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_21, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_22, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_22, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_23, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_23, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_24, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_24, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_25, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_25, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_26, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_26, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_27, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_27, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_28, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_28, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_29, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_29, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_30, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_30, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_31, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_31, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigaction(SIGRT_32, NULL, {sa_handler=SIG_DFL, sa_mask=[], sa_flags=0}, 8) = 0
rt_sigaction(SIGRT_32, {sa_handler=0x45faa0, sa_mask=~[], sa_flags=SA_RESTORER|SA_ONSTACK|SA_RESTART|SA_SIGINFO, sa_restorer=0x45fbe0}, NULL, 8) = 0
rt_sigprocmask(SIG_SETMASK, ~[], [], 8) = 0
clone(child_stack=0xc000046000, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS, tls=0xc000036090) = 1233
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
rt_sigprocmask(SIG_SETMASK, ~[], [], 8) = 0
clone(child_stack=0xc000048000, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS, tls=0xc000036490) = 1234
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
rt_sigprocmask(SIG_SETMASK, ~[], [], 8) = 0
clone(child_stack=0xc000042000, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS, tls=0xc000036890) = 1235
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
futex(0x56b0e8, FUTEX_WAIT_PRIVATE, 0, NULL) = 0
rt_sigprocmask(SIG_SETMASK, ~[], [], 8) = 0
clone(child_stack=0xc000044000, flags=CLONE_VM|CLONE_FS|CLONE_FILES|CLONE_SIGHAND|CLONE_THREAD|CLONE_SYSVSEM|CLONE_SETTLS, tls=0xc000036c90) = 1236
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
futex(0x56b0e8, FUTEX_WAIT_PRIVATE, 0, NULL) = 0
fcntl(0, F_GETFL)                       = 0x2 (flags O_RDWR)
mmap(NULL, 262144, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f2b60d7b000
fcntl(1, F_GETFL)                       = 0x2 (flags O_RDWR)
fcntl(2, F_GETFL)                       = 0x2 (flags O_RDWR)
getuid()                                = 1000
openat(AT_FDCWD, "/etc/passwd", O_RDONLY|O_CLOEXEC) = 3
epoll_create1(EPOLL_CLOEXEC)            = 4
pipe2([5, 6], O_NONBLOCK|O_CLOEXEC)     = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
epoll_ctl(4, EPOLL_CTL_ADD, 5, {EPOLLIN, {u32=5871088, u64=5871088}}) = 0
--- SIGURG {si_signo=SIGURG, si_code=SI_TKILL, si_pid=1231, si_uid=1000} ---
rt_sigreturn({mask=[]})                 = 0
epoll_ctl(4, EPOLL_CTL_ADD, 3, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=1624784568, u64=139824285105848}}) = -1 EPERM (Operation not permitted)
read(3, "root:x:0:0:root:/root:/bin/bash\n"..., 4096) = 1583
close(3)                                = 0
newfstatat(AT_FDCWD, "/home/admin/data/newdatafile", {st_mode=S_IFREG|0644, st_size=1500000000, ...}, 0) = 0
unlinkat(AT_FDCWD, "/home/admin/data/newdatafile", 0) = 0
newfstatat(AT_FDCWD, "/usr/local/sbin/fallocate", 0xc0000902a8, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/local/bin/fallocate", 0xc000090378, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/sbin/fallocate", 0xc000090448, 0) = -1 ENOENT (No such file or directory)
newfstatat(AT_FDCWD, "/usr/bin/fallocate", {st_mode=S_IFREG|0755, st_size=35048, ...}, 0) = 0
openat(AT_FDCWD, "/dev/null", O_RDONLY|O_CLOEXEC) = 3
epoll_ctl(4, EPOLL_CTL_ADD, 3, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=1624784568, u64=139824285105848}}) = -1 EPERM (Operation not permitted)
openat(AT_FDCWD, "/dev/null", O_WRONLY|O_CLOEXEC) = 7
epoll_ctl(4, EPOLL_CTL_ADD, 7, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=1624784568, u64=139824285105848}}) = -1 EPERM (Operation not permitted)
openat(AT_FDCWD, "/dev/null", O_WRONLY|O_CLOEXEC) = 8
epoll_ctl(4, EPOLL_CTL_ADD, 8, {EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET, {u32=1624784568, u64=139824285105848}}) = -1 EPERM (Operation not permitted)
pipe2([9, 10], O_CLOEXEC)               = 0
getpid()                                = 1231
rt_sigprocmask(SIG_SETMASK, NULL, [], 8) = 0
rt_sigprocmask(SIG_SETMASK, ~[], NULL, 8) = 0
clone(child_stack=NULL, flags=CLONE_VM|CLONE_VFORK|SIGCHLD) = 1238
rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
close(10)                               = 0
read(9, "", 8)                          = 0
close(9)                                = 0
close(3)                                = 0
close(7)                                = 0
close(8)                                = 0
waitid(P_PID, 1238, {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=1238, si_uid=1000, si_status=0, si_utime=0, si_stime=0}, WEXITED|WNOWAIT, NULL) = 0
--- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=1238, si_uid=1000, si_status=0, si_utime=0, si_stime=0} ---
rt_sigreturn({mask=[]})                 = 0
wait4(1238, [{WIFEXITED(s) && WEXITSTATUS(s) == 0}], 0, {ru_utime={tv_sec=0, tv_usec=2268}, ru_stime={tv_sec=0, tv_usec=0}, ...}) = 1238
write(1, "Done.\n", 6Done.
)                  = 6
exit_group(0)                           = ?
+++ exited with 0 +++
```

a new file is created:

```
admin@i-05cccd0e68ed9feca:~/data$ ls -alt
total 1464856
drwxr-xr-x 2 admin root        4096 Mar 31 15:42 .
-rw-r--r-- 1 admin admin 1500000000 Mar 31 15:42 newdatafile
drwxr-xr-x 7 admin admin       4096 Mar 31 15:35 ..
```

so we found the problem is not enough disk space.

10. create new logical volume for `/home/admin/data`

```
admin@i-0e335d46fe5482627:~$ lsblk
NAME         MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
nvme0n1      259:0    0    8G  0 disk 
├─nvme0n1p1  259:1    0  7.9G  0 part /
├─nvme0n1p14 259:2    0    3M  0 part 
└─nvme0n1p15 259:3    0  124M  0 part /boot/efi
nvme2n1      259:4    0    1G  0 disk 
nvme1n1      259:5    0    1G  0 disk 
admin@i-0e335d46fe5482627:~$ sudo pvcreate nvme2n1 nvme1n1
  No device found for nvme2n1.
  No device found for nvme1n1.
admin@i-0e335d46fe5482627:~$ sudo pvcreate /dev/nvme2n1 /dev/nvme1n1
  Physical volume "/dev/nvme2n1" successfully created.
  Physical volume "/dev/nvme1n1" successfully created.
admin@i-0e335d46fe5482627:~$ sudo vgcreate my_vg /dev/nvme2n1 /dev/nvme1n1
  Volume group "my_vg" successfully created
admin@i-0e335d46fe5482627:~$ sudo lvcreate -L 1.9G -n my_lv my_vg
  Logical volume "my_lv" created.
admin@i-0e335d46fe5482627:~$ sudo mkfs.ext4 /dev/my_vg/my_lv
mke2fs 1.46.2 (28-Feb-2021)
Creating filesystem with 393216 4k blocks and 98304 inodes
Filesystem UUID: 92a104b7-48ee-43bd-94f3-bc889dfd9bec
Superblock backups stored on blocks: 
        32768, 98304, 163840, 229376, 294912

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (8192 blocks): done
Writing superblocks and filesystem accounting information: done 

admin@i-0e335d46fe5482627:~$ sudo mount /dev/my_vg/my_lv ~/data
```

### Futher Study

- Logical Volume Manager
