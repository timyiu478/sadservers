## "Venice": Am I in a container?

### Problem

> Try and figure out if you are inside a container (like a Docker one for example) or inside a Virtual Machine (like in the other scenarios).

https://sadservers.com/scenario/venice

### Solution

```
root@i-032fff63ae5fe83c4:/# systemd-detect-virt -v
kvm
```
