## "Minneapolis with a Vengeance": Break a CSV file

### Problem

https://sadservers.com/scenario/minneapolis-2

### Solution

1. convert the file from windows format to unix format

```
admin@i-00573bd958c1dc781:~$ dos2unix data.csv
dos2unix: converting file data.csv to Unix format...
```

2. break the csv using python script

TLDR: (1) append header for each partitioned csv; (2) sort rows of data.csv in terms of row size; (3) for row in rows, append the row to the file withe least file size with the help of min heap data structure.

source code: [break_csv.py](../script/break_csv.py)
