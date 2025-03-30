## "Oaxaca": Close an Open File

### Problem

> The file `/home/admin/somefile` is open for writing by some process. Close this file without killing the process.

https://sadservers.com/scenario/oaxaca

### Solution

1. use `fuser` to know which process open `somefile`

PID: 1017

```
admin@i-05d529ee5b6eb02b2:/$ fuser -v /home/admin/somefile
                     USER        PID ACCESS COMMAND
/home/admin/somefile:
                     admin       844 F.... bash
```

2. check avaliable signals that can interact with the process

```
admin@i-0845c4cd4364b8ab8:/$ fuser -l /home/admin/somefile
HUP INT QUIT ILL TRAP ABRT BUS FPE KILL USR1 SEGV USR2 PIPE ALRM TERM STKFLT
CHLD CONT STOP TSTP TTIN TTOU URG XCPU XFSZ VTALRM PROF WINCH POLL PWR SYS
```

3. try to send `HUP` signal

```
admin@i-0845c4cd4364b8ab8:/$ kill -1 844
```
