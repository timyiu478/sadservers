## "Yokohama": Linux Users Working Together

### Problem

https://sadservers.com/scenario/yokohama

### Solution

1. create group `project`

```
admin@i-088880a1c1b9ce1cb:~/shared$ sudo groupadd project
```

2. add them into group `project`

```
admin@i-088880a1c1b9ce1cb:~/shared$ sudo usermod --append --groups project abe
admin@i-088880a1c1b9ce1cb:~/shared$ sudo usermod --append --groups project betty
admin@i-088880a1c1b9ce1cb:~/shared$ sudo usermod --append --groups project carlos
admin@i-088880a1c1b9ce1cb:~/shared$ sudo usermod --append --groups project debora
```

3. change their personal files group to `project`

```
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chgrp project project_abe 
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chgrp project project_betty 
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chgrp project project_carlos 
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chgrp project project_debora 
admin@i-088880a1c1b9ce1cb:~/shared$ ls -alt
total 28
drwxr-xr-x 6 admin  admin   4096 Apr  2 05:50 ..
drwxr-xr-x 2 admin  admin   4096 Feb  2 16:06 .
-rw-r--r-- 1 root   admin     38 Feb  2 16:06 ALL
-rw-r----- 1 debora project   30 Feb  2 16:06 project_debora
-rw-r----- 1 carlos project   30 Feb  2 16:06 project_carlos
-rw-r----- 1 betty  project   29 Feb  2 16:06 project_betty
-rw-r----- 1 abe    project   27 Feb  2 16:06 project_abe
```

4. change file `ALL`  attributes on a Linux file system to append only

```
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chgrp project ALL
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chmod 664 ALL
admin@i-088880a1c1b9ce1cb:~/shared$ sudo chattr +a ALL
```

Ref: https://man7.org/linux/man-pages/man1/chattr.1.html
