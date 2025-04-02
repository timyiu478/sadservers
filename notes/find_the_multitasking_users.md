## "Hanoi": Find the Multitasking Users

### Problem

https://sadservers.com/scenario/hanoi

### Solution

```
admin@i-08b596ed7940ffa1d:~$ for u in $(cat users.txt); do [ $(grep "[:,]$u" groups.txt | wc -l) -gt 1 ] && echo "$u" >> multi-group-users.txt; done
admin@i-08b596ed7940ffa1d:~$ cat multi-group-users.txt 
bob
charlie
```
