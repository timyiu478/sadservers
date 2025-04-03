## "Manado": How much do you press?

### Problem

https://sadservers.com/scenario/manado

### Solution

1. sort the names for the compressor easier to find patterns

```
admin@i-0c5060f42959c9124:~$ cat names | sort -d > sorted_names
```


2. compress the file using `xz` command

```
xz -8 -e sorted_names
```
