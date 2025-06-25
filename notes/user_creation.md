## "Budapest": User Creation

### Problem

Given the file `user_list.txt` you must create all the users specified in the file with their corresponding passwords.

The entries in the user_list.txt file are stored as `username;password`

https://sadservers.com/scenario/budapest

### Solution

add them by writing a simple bash script

```bash
USERS=$(cat user_list.txt)

for user in $USERS; do
  IFS=';' read -r newuser newpw <<< "$user"
  sudo useradd -m -p $(openssl passwd -1 -salt "$newpw" "$newpw") "$newuser"
done
```
