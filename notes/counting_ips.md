## #Saskatoon": counting IPs.

### Problem

https://sadservers.com/newserver/saskatoon

## Solution

Command: `awk -F' ' '{print $1}' /home/admin/access.log | sort | uniq -c | sort`

Explanation:

1. `awk -F' ' '{print $1}' /home/admin/access.log`: get the list of IPs
2. `sort`: sort them(list of IPs with redundancy) in alphabetical descending order
3. `uniq -c`: counts the occurrences of each unique IP
4. `sort`: sort them(list of uniq IPs) in alphabetical descending order

Why step 2? Because `uniq` command won't detect duplicates unless they are adjacent.
