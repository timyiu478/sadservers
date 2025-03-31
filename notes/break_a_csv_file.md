## "Minneapolis": Break a CSV file

### Problem

https://sadservers.com/newserver/minneapolis

### Solution

1. check the size of data.csv

```
admin@i-0159f81fac4f20334:~$ cat data.csv | wc -c
312715
```

2. split data.csv to data-0{0..9}.csv

```
admin@i-0159f81fac4f20334:~$ split -b 31000 -d --additional-suffix=.csv data.csv data-
```

3. prepend header to data-{1..9}.csv

```
admin@i-0159f81fac4f20334:~$ for i in {1..9}; do head -n 1 data.csv | cat - "data-0$i.csv" > temp && mv temp "data-0$i.csv"; done
```
