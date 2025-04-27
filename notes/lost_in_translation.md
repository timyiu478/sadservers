## Bharuch: "Lost in Translation"

### Problem

There's a Docker container that runs a web server on port 3000, but it's not working.

Using the tooling and resources provided in the server, make the container run correctly.

https://sadservers.com/scenario/bharuch

### Solution

1. try to curl

```
admin@i-0f608dc455b47e831:~$ curl -vv http://localhost:3000
*   Trying 127.0.0.1:3000...
* connect to 127.0.0.1 port 3000 failed: Connection refused
* Failed to connect to localhost port 3000: Connection refused
* Closing connection 0
curl: (7) Failed to connect to localhost port 3000: Connection refused
```

2. check if the web server is running

restarting

```
admin@i-0f608dc455b47e831:~$ docker ps 
CONTAINER ID   IMAGE               COMMAND                  CREATED        STATUS                            PORTS     NAMES
3e2e878ab10c   web-server:latest   "/bin/sh -c 'python …"   22 hours ago   Restarting (255) 36 seconds ago             web-server
```

3. check the container logs

exec /bin/sh: exec format error

```
admin@i-0f608dc455b47e831:~$ docker logs 3e2e878ab10c
exec /bin/sh: exec format error
exec /bin/sh: exec format error
exec /bin/sh: exec format error
exec /bin/sh: exec format error
exec /bin/sh: exec format error
exec /bin/sh: exec format error
exec /bin/sh: exec format error
```

4. check how the web-server docker image was built

It seems the base image OS runs on `arm64` architecture.

```
8dc455b47e831:/var/lib/docker/overlay2/f75564f38d2592d5ceb633ec5ad8cf76f25f5bc227c80ae99786283c381ed75c-init# docker history web-server
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
ec84d7ad1a81   6 weeks ago     CMD ["/bin/sh" "-c" "python app.py"]            0B        buildkit.dockerfile.v0
<missing>      6 weeks ago     RUN /bin/sh -c pip install -r requirements.t…   11.5MB    buildkit.dockerfile.v0
<missing>      6 weeks ago     COPY app.py requirements.txt ./ # buildkit      391B      buildkit.dockerfile.v0
<missing>      6 weeks ago     WORKDIR /app                                    0B        buildkit.dockerfile.v0
<missing>      4 months ago    CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      4 months ago    RUN /bin/sh -c set -eux;  for src in idle3 p…   36B       buildkit.dockerfile.v0
<missing>      4 months ago    RUN /bin/sh -c set -eux;   wget -O python.ta…   54.2MB    buildkit.dockerfile.v0
<missing>      4 months ago    ENV PYTHON_SHA256=3126f59592c9b0d798584755f2…   0B        buildkit.dockerfile.v0
<missing>      4 months ago    ENV PYTHON_VERSION=3.9.21                       0B        buildkit.dockerfile.v0
<missing>      4 months ago    ENV GPG_KEY=E3FF2839C048B25C084DEBE9B26995E3…   0B        buildkit.dockerfile.v0
<missing>      4 months ago    RUN /bin/sh -c set -eux;  apt-get update;  a…   18.2MB    buildkit.dockerfile.v0
<missing>      4 months ago    ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      4 months ago    ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      15 months ago   RUN /bin/sh -c set -ex;  apt-get update;  ap…   560MB     buildkit.dockerfile.v0
<missing>      15 months ago   RUN /bin/sh -c set -eux;  apt-get update;  a…   183MB     buildkit.dockerfile.v0
<missing>      23 months ago   RUN /bin/sh -c set -eux;  apt-get update;  a…   48.5MB    buildkit.dockerfile.v0
<missing>      23 months ago   # debian.sh --arch 'arm64' out/ 'bookworm' '…   139MB     debuerreotype 0.15
```

5. check the machine cpu architecture

`x86_64` instead of `arm64`

```
admin@i-02614291fc20a77b0:~$ uname -a
linux i-02614291fc20a77b0 5.10.0-33-cloud-amd64 #1 smp debian 5.10.226-1 (2024-10-03) x86_64 gnu/linux
admin@i-02614291fc20a77b0:~$ docker version
client: docker engine - community
 version:           28.1.1
 api version:       1.49
 go version:        go1.23.8
 git commit:        4eba377
 built:             fri apr 18 09:52:29 2025
 os/arch:           linux/amd64
 context:           default

server: docker engine - community
 engine:
  version:          28.1.1
  api version:      1.49 (minimum version 1.24)
  go version:       go1.23.8
  git commit:       01f442b
  built:            fri apr 18 09:52:29 2025
  os/arch:          linux/amd64
  experimental:     false
 containerd:
  version:          1.7.27
  gitcommit:        05044ec0a9a75232cad458027ca83437aae3f4da
 runc:
  version:          1.2.5
  gitcommit:        v1.2.5-0-g59923ef
 docker-init:
  version:          0.19.0
  gitcommit:        de40ad0
```

6. run the qume for setting up the emulation for running the arm64 architecture on amd64 host

```
root@i-02614291fc20a77b0:~# docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

7. check if the emulation is enabled

```
admin@i-0eb28cafec9c0a80b:~$ ps -aux | grep qemu
root        2496  0.0  1.7 154672  8280 ?        Ssl  14:36   0:00 /usr/bin/qemu-aarch64-static /bin/sh -c python app.py
root        2538  1.1 12.8 193616 60048 ?        Sl   14:36   0:04 /usr/bin/qemu-aarch64-static /usr/local/bin/python app.py
```

# Lesson Learnt

The directory `/proc/sys/fs/binfmt_misc` is where the kernel manages binary format handlers (binfmt) for supporting **non-native** binaries. Binfmt allows the system to automatically determine how to execute files based on their formats, such as ELF binaries for specific architectures.
