## "Ivujivik": Parlez-vous Français?

### Problem

> Given the CSV file /home/admin/table_tableau11.csv, find the Electoral District Name/Nom de circonscription that has the largest number of Rejected Ballots/Bulletins rejetés and also has a population of less than 100,000. **The initial CSV file may be corrupted or invalid in a way that can be fixed without changing its data.**

https://sadservers.com/scenario/ivujivik

### Solution

1. 

```
admin@i-041683760f6b4ece7:~$ mlr --csv sort -f 'Rejected Ballots/Bulletins rejetés' table_tableau11.csv 
mlr: Header/data length mismatch (13 != 12) at file "table_tableau11.csv" line 101
```

2.
    1. Filter: Selects rows where the Population < 100000.
    2. Sort: Orders the filtered rows by descending values in "Rejected Ballots/Bulletins rejetés".
    3. Head: Retrieves the top row (i.e., the one with the maximum value).
    4. Cut: Extracts only the "Electoral District Name/Nom de circonscription" column.

```
admin@i-010ac90ddec6ae72f:~$ mlr --csv filter '$Population < 100000' then sort -nr "Rejected Ballots/Bulletins rejetés" then head -n 1 then cut -f "Electoral District Name/Nom de circonscription" table_tableau11.csv
Electoral District Name/Nom de circonscription
Montcalm
```

Note:

Miller is a command-line tool for querying, shaping, and reformatting data files in various formats including CSV, TSV, JSON, and JSON Lines. https://miller.readthedocs.io/en/latest/
