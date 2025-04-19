## "Belo-Horizonte": A Java Enigma

### Problem

There is a one-class Java application in your /home/admin directory. Running the program will print out a secret code, or you may be able to extract the secret from the class file without executing it but I'm not providing any special tools for that.

Put the secret code in a /home/admin/solution file, eg echo "code" > /home/admin/solution.

https://sadservers.com/scenario/belo-horizonte

### Solution

1. find the Java class

```
admin@i-0f9fb27157a46ea91:~$ ls 
Sad.class  agent
```

2. try to run this class by JVM

```
admin@i-0f9fb27157a46ea91:~$ java Sad
Error: LinkageError occurred while loading main class Sad
        java.lang.UnsupportedClassVersionError: Sad has been compiled by a more recent version of the Java Runtime (class file version 61.0), this version of the Java Runtime only recognizes class file versions up to 55.0
```

3. upgrade to java 17 from java 11

```
admin@i-0f9fb27157a46ea91:/bin$ sudo update-alternatives --config java
There are 2 choices for the alternative java (providing /usr/bin/java).

  Selection    Path                                         Priority   Status
------------------------------------------------------------
  0            /usr/lib/jvm/java-17-openjdk-amd64/bin/java   1711      auto mode
  1            /usr/lib/jvm/java-11-openjdk-amd64/bin/java   1111      manual mode
  2            /usr/lib/jvm/java-17-openjdk-amd64/bin/java   1711      manual mode

Press <enter> to keep the current choice[*], or type selection number: 0
update-alternatives: using /usr/lib/jvm/java-17-openjdk-amd64/bin/java to provide /usr/bin/java (java) in auto mode
admin@i-0f9fb27157a46ea91:/bin$ java --version
openjdk 17.0.6 2023-01-17
OpenJDK Runtime Environment (build 17.0.6+10-Debian-1deb11u1)
OpenJDK 64-Bit Server VM (build 17.0.6+10-Debian-1deb11u1, mixed mode, sharing)
```

4. run the Sad.class by JVM 17

The public class name needs to match the filename.
It ensures that the compiler and runtime can uniquely identify and associate the source code file with the correct class definition.

```
admin@i-0f9fb27157a46ea91:~$ java Sad 
Error: Could not find or load main class Sad
Caused by: java.lang.NoClassDefFoundError: VerySad (wrong name: Sad)
```

5. `cp Sad.class VerySad.class`

```
admin@i-0f9fb27157a46ea91:~$ cp Sad.class VerySad.class
admin@i-0f9fb27157a46ea91:~$ java VerySad 
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
        at VerySad.main(VerySad.java:4)
```

6. try to increase max heap limit

```
admin@i-0f9fb27157a46ea91:~$ java -Xms512m -Xms1g VerySad
OpenJDK 64-Bit Server VM warning: INFO: os::commit_memory(0x00000000d5550000, 715849728, 0) failed; error='Not enough space' (errno=12)
#
# There is insufficient memory for the Java Runtime Environment to continue.
# Native memory allocation (mmap) failed to map 715849728 bytes for committing reserved memory.
# An error report file with more information is saved as:
# /home/admin/hs_err_pid1486.log
```

7. check how much free memory

No swap space

```
admin@i-0f9fb27157a46ea91:~$ free -ghw
               total        used        free      shared     buffers       cache   available
Mem:           455Mi        81Mi       266Mi       0.0Ki       4.0Mi       103Mi       361Mi
Swap:             0B          0B          0B
```

8. add swap space

```
admin@i-063ca134faa4ce432:~$ fallocate -l 3G ./swapgile # allocate 3GB disk space to swapgile file
admin@i-063ca134faa4ce432:~$ mkswap swapgile # set up swap space on file swapgile
admin@i-063ca134faa4ce432:~$ sudo swapon swapgile # enable swapgile file for swapping
admin@i-063ca134faa4ce432:~$ swapon --show
NAME                 TYPE SIZE USED PRIO
/home/admin/swapgile file   3G   0B   -2
admin@i-063ca134faa4ce432:~$ free -h
               total        used        free      shared  buff/cache   available
Mem:           455Mi        83Mi       297Mi       0.0Ki        73Mi       359Mi
Swap:          3.0Gi          0B       3.0Gi
```
