## "Unimak Island": Fun with Mr Jason

### Problem

> Using the file station_information.json , find the station_id where "has_kiosk" is false and "capacity" is greater than 30

https://sadservers.com/scenario/unimak

### Solution

run

```
jq '.data.stations[] | select(.has_kiosk == false and .capacity > 30) | .station_id' < station_information.json
```
