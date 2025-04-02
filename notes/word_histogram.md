## "Marrakech": Word Histogram

### Problem

https://sadservers.com/scenario/marrakech

### Solution

1. write a python script to split the text into words

```
admin@i-01420286e65da0f4c:~$ cat split.py 
#!/usr/bin/python3

import re

with open("/home/admin/frankestein.txt") as file:
    data = file.read().rstrip()
    words = re.split('[.,:; \n]', data)
    for word in words:
        print(word)
admin@i-0bb2f923154238f7a:~$ chmod +x split.py 
```

2. pipe with the gnu tools to get the second most frequently used word

```
admin@i-0bb2f923154238f7a:~$ ./split.py | sort | uniq -c | sort | tr a-z A-Z | tail -n 5
   2747 OF
   2758 I
   2990 AND
   4066 THE
  10080
```
