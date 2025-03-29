## "Apia": Needle in a Haystack

### Problem

https://sadservers.com/newserver/apia

### Solution

1. find the uniq checksums of the files

```
admin@i-0ed2876b4f94898bd:~/data$ for f in $(ls); do md5sum "$f" | awk -F' ' '{print $1}'; done | sort | uniq -c 
      1 7cb9ff9334dcaac970ff366a2f652eb1
    100 9d8f6e03f124eae74cdd260a6e8356fa
```

2. find the file with checksum `7cb9ff9334dcaac970ff366a2f652eb1`

```
admin@i-0ed2876b4f94898bd:~/data$ for f in $(ls); do md5sum "$f"; done | grep 7cb
7cb9ff9334dcaac970ff366a2f652eb1  file76.txt
```

3. find the differences between `file76.txt` and other texts using `diff` command

```
admin@i-0ed2876b4f94898bd:~/data$ diff file76.txt file1.txt 
3c3
< Porttitor neque laoreet pharetra condimentum per imperdiet montes mollis, hendrerit bibendum nullam nostra nec faucibus phasellus luctus, ac fringilla lacinia rutrum senectus dui non. Iaculis conubia suscipit montes fames dapibus leo eleifend imperdiet aliquam, fringilla mi tempor vivamus pulvinar sollicitudin at volutpat, eureka habitant hendrerit vehicula lobortis neque auctor proin cursus. Venenatis porttitor neque ad facilisi porta mus, hendrerit feugiat quis gravida purus accumsan, duis vulputate convallis posuere habitasse.
---
> Porttitor neque laoreet pharetra condimentum per imperdiet montes mollis, hendrerit bibendum nullam nostra nec faucibus phasellus luctus, ac fringilla lacinia rutrum senectus dui non. Iaculis conubia suscipit montes fames dapibus leo eleifend imperdiet aliquam, fringilla mi tempor vivamus pulvinar sollicitudin at volutpat, habitant hendrerit vehicula lobortis neque auctor proin cursus. Venenatis porttitor neque ad facilisi porta mus, hendrerit feugiat quis gravida purus accumsan, duis vulputate convallis posuere habitasse.
\ No newline at end of file
```

eureka
