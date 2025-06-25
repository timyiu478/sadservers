## "Tokelau": Delete from history

### Problem

The objective of this exercise is to delete all the Bash history lines that contain the term foo.

Clearing out or deleting the history file /home/admin/.bash_history is now allowed. Note that in our case, new commands (including the ones to try and delete "foo" from history) are also appended to the history file.

Source: https://sadservers.com/scenario/tokelau

### Solution

1. grep the line numbers of history commands that contain "foo" in reverse order

The reason of deleting commands in reverse order is we want to avoid the corruption of the history line numbers we will delete.

```
for i in $(history | grep 'foo' | awk '{ print $1 }' | tac)
do 
  history -d "$i"
done
```

2. write the in memory session history back to `~/.bash_history` file

```
history -w
```
