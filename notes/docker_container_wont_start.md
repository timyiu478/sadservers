## "Salta": Docker container won't start.

### Problem

> There's a "dockerized" Node.js web application in the /home/admin/app directory. Create a Docker container so you get a web app on port :8888 and can curl to it. For the solution to be valid, there should be only one running Docker container.

https://sadservers.com/scenario/salta

### Solution

1. view the Dockerfile

Exposed port: 8880

```
admin@i-09d715ebe2431be41:~/app$ cat Dockerfile 
# documentation https://nodejs.org/en/docs/guides/nodejs-docker-webapp/

# most recent node (security patches) and alpine (minimal, adds to security, possible libc issues)
FROM node:15.7-alpine 

# Create app directory & copy app files
WORKDIR /usr/src/app

# we copy first package.json only, so we take advantage of cached Docker layers
COPY ./package*.json ./

# RUN npm ci --only=production
RUN npm install

# Copy app source
COPY ./* ./

# port used by this app
EXPOSE 8880

# command to run
CMD [ "node", "serve.js" ]
```

2. rm the old docker images

```
admin@i-0dbb9eb58da6a37cc:~/app$ sudo docker image rm app node
Untagged: app:latest
Deleted: sha256:1d782b86d6f26b0877ec646f695c050c0347e9ed41cf14e2b4eda1d3f6c0b06c
Deleted: sha256:0b18357df7c95d4e5d99b59bfbad1c90092e14ea76603a500fe66e276fc6de44
Deleted: sha256:a6ee5c4d5a96af476985f6c7596f152587ec63b0c7bc5601d1ccdac4b7514d7a
Deleted: sha256:d88262941a0348515f949bb314d58295f89e99cecb84308a9a63b225f1900b3d
Deleted: sha256:5cad5aa08c7a60f0710d6ca2315269efd97fd0bb44c2f8615753d98a8c503506
Deleted: sha256:6a2223e3989e957e90bac06503273f9a0c41c6f442bfc695e01911bc3cf58ad7
Deleted: sha256:acfb467c80ba1bf1ab7a41954db5d963186d0ad55c898efe9267f2f1fa46ec11
Deleted: sha256:305f2ab7d203b5699c1bfe409c5a007ef37baadf689a0eb79586e61ace289033
Deleted: sha256:463b1571f18ef0a953158bd436ac539a66468f61b4e94a86de0fd8ae30fe4db1
Deleted: sha256:b6fa064ade8f5ca9f97f55b192b94fecebe8a695a90b680f93dc0957e8772693
```

```
admin@i-0dbb9eb58da6a37cc:~/app$ sudo docker image rm node:15.7-alpine
Untagged: node:15.7-alpine
Untagged: node@sha256:f9d36cc9a6fa414a98db937c31d7df1c73c18db8195ed431ac7f37e15d103d18
Deleted: sha256:706d12284dd5e9b1ab3e82dfe76316c9827cf53fb89bee481d9743fef8bad6e1
Deleted: sha256:d2560ae7d8f85ae0c8c0ca3911f6d10401966afd65571b075db7a9c121a2d173
Deleted: sha256:9594e8d9f36b3e74cd31c5a65c597da15fcc2c66c114135f9d7d501da3b2ab01
Deleted: sha256:6a77e480d129d13d87db488fac56c11fa8fc6547d759514a1cf0d94f12e2b15c
Deleted: sha256:0fcbbeeeb0d7fc5c06362d7a6717b999e605574c7210eff4f7418f6e9be9fbfe
```


3. build docker image

```
admin@i-09d715ebe2431be41:~$ sudo docker build -t app app
Sending build context to Docker daemon  101.9kB
Step 1/7 : FROM node:15.7-alpine
 ---> 706d12284dd5
Step 2/7 : WORKDIR /usr/src/app
 ---> Using cache
 ---> 463b1571f18e
Step 3/7 : COPY ./package*.json ./
 ---> Using cache
 ---> acfb467c80ba
Step 4/7 : RUN npm install
 ---> Using cache
 ---> 5cad5aa08c7a
Step 5/7 : COPY ./* ./
 ---> Using cache
 ---> a6ee5c4d5a96
Step 6/7 : EXPOSE 8880
 ---> Using cache
 ---> 0b18357df7c9
Step 7/7 : CMD [ "node", "serve.js" ]
 ---> Using cache
 ---> 1d782b86d6f2
Successfully built 1d782b86d6f2
```

4. try to run the docker image

```
admin@i-09d715ebe2431be41:~$ sudo docker run -p 8888:8880 app
docker: Error response from daemon: driver failed programming external connectivity on endpoint kind_euler (96c1fab4a7cd5fd5eb05c7231bba33a6c2286e9577f482033f524698a8964983): Error starting userland proxy: listen tcp4 0.0.0.0:8888: bind: address already in use.
ERRO[0000] error waiting for container: context canceled 
```

5. find the process using the tcp socket

```
admin@i-09d715ebe2431be41:~$ sudo netstat -tulnp
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      592/sshd: /usr/sbin 
tcp        0      0 0.0.0.0:8888            0.0.0.0:*               LISTEN      606/nginx: master p 
```

6. kill process 606

```
admin@i-09d715ebe2431be41:~$ sudo kill -9 606
```

7. try to run the docker image again



```
admin@i-0dbb9eb58da6a37cc:~$ sudo docker run -p 8888:8880 app
node:internal/modules/cjs/loader:928
  throw err;
  ^

Error: Cannot find module '/usr/src/app/serve.js'
    at Function.Module._resolveFilename (node:internal/modules/cjs/loader:925:15)
    at Function.Module._load (node:internal/modules/cjs/loader:769:27)
    at Function.executeUserEntryPoint [as runMain] (node:internal/modules/run_main:76:12)
    at node:internal/main/run_main_module:17:47 {
  code: 'MODULE_NOT_FOUND',
  requireStack: []
}
```

8. fix the docker file typo and rebuild the image

should be `server.js` instead of `serve.js`

```
CMD [ "node", "server.js" ]
```

9. try to curl

Connection reset by peer

```
admin@i-0dbb9eb58da6a37cc:/$ curl -v localhost:8888
*   Trying 127.0.0.1:8888...
* Connected to localhost (127.0.0.1) port 8888 (#0)
> GET / HTTP/1.1
> Host: localhost:8888
> User-Agent: curl/7.74.0
> Accept: */*
> 
* Recv failure: Connection reset by peer
* Closing connection 0
curl: (56) Recv failure: Connection reset by peer
```

10. update dockerfile and server.js to ensure they expose `8888` container port and rebuild the image

Dockerfile:

```
# port used by this app
EXPOSE 8888
```

server.js:

```
var express = require('express'),
  app = express(),
  port = 8888,
  bodyParser = require('body-parser');
```

11. run the docker image with the same host and container port

```
admin@i-0dbb9eb58da6a37cc:~$ sudo docker run -p 8888:8888 app
```
