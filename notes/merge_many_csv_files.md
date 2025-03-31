## "Saint Paul": Merge Many CSVs files

### Problem

https://sadservers.com/newserver/st-paul

### Solution

1. copy the header to all.csv

```
admin@i-0f42dfeec49d755ef:~$ head -n 1 polldayregistrations_enregistjourduscrutin62001.csv > all.csv
```

2. copy the non header content of each file to all.csv

```
admin@i-0f42dfeec49d755ef:~$ export header=$(head -n 1 polldayregistrations_enregistjourduscrutin62001.csv)
admin@i-0f42dfeec49d755ef:~$ for f in "$(ls *.csv)"; do grep -vhs $header $f >> all.csv; done
```
