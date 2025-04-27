## "Quito": Control One Container from Another

### Problem

You have a running container named docker-access. Another container nginx is present but in a stopped state. Your goal is to start the nginx container from inside the docker-access container.

You must not start the nginx container from the host system or any other container that is not docker-access. You can restart this docker-access container.

https://sadservers.com/scenario/quito

### Solution

1. understand a bit more about `docker-access`

```
admin@i-0377ecb032eae0794:~$ docker history docker-access
IMAGE          CREATED        CREATED BY                                      SIZE      COMMENT
2e2a2271540d   6 weeks ago    CMD ["sh"]                                      0B        buildkit.dockerfile.v0
<missing>      6 weeks ago    WORKDIR /usr/src/app                            0B        buildkit.dockerfile.v0
<missing>      6 weeks ago    RUN /bin/sh -c apk add --no-cache docker-cli…   30.3MB    buildkit.dockerfile.v0
<missing>      2 months ago   CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      2 months ago   ADD alpine-minirootfs-3.21.3-x86_64.tar.gz /…   7.83MB    buildkit.dockerfile.v0
```

2. run a shell in `docker-access`


```
admin@i-0377ecb032eae0794:~$ docker run -it docker-access sh
```

3. try to list docker image inside container

```
/usr/src/app # docker image ls
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

4. remove the old docker-access container

```
$ docker rm docker-access
```

5. run a shell in `docker-access` and bind the docker daemon socket

```
admin@i-0377ecb032eae0794:~$ docker run -v /var/run/docker.sock:/var/run/docker.sock --name docker-access -it docker-access sh
/usr/src/app # docker image ls
REPOSITORY      TAG       IMAGE ID       CREATED       SIZE
nginx           latest    4e1b6bae1e48   11 days ago   192MB
docker-access   latest    2e2a2271540d   6 weeks ago   38.2MB
```

6. restart nginx

```
/usr/src/app # docker restart nginx
```
