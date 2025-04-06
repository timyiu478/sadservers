## "Singara": Docker and Kubernetes web app not working.

### Problem

> There's a k3s Kubernetes install you can access with kubectl. The Kubernetes YAML manifests under /home/admin have been applied. The objective is to access from the host the "webapp" web server deployed and find what message it serves (it's a name of a town or city btw). In order to pass the check, the webapp Docker container should not be run separately outside Kubernetes as a shortcut.

https://sadservers.com/scenario/singara

### Solution

1. try to curl

```
admin@i-056e412b0fa3fba26:/$ curl -vvvv localhost:8888
*   Trying 127.0.0.1:8888...
* connect to 127.0.0.1 port 8888 failed: Connection refused
* Failed to connect to localhost port 8888: Connection refused
* Closing connection 0
curl: (7) Failed to connect to localhost port 8888: Connection refused
```

2. check process listen to port 8888

No process listent to port 8888.

```
admin@i-056e412b0fa3fba26:/$ sudo netstat -tlnp 
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 127.0.0.1:10256         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 127.0.0.1:10257         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 127.0.0.1:10258         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 127.0.0.1:10259         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      606/sshd: /usr/sbin 
tcp        0      0 127.0.0.1:10010         0.0.0.0:*               LISTEN      983/containerd      
tcp        0      0 127.0.0.1:10248         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 127.0.0.1:10249         0.0.0.0:*               LISTEN      608/k3s server      
tcp        0      0 127.0.0.1:6444          0.0.0.0:*               LISTEN      608/k3s server      
tcp6       0      0 :::8080                 :::*                    LISTEN      575/gotty           
tcp6       0      0 :::37493                :::*                    LISTEN      1035/promtail       
tcp6       0      0 :::22                   :::*                    LISTEN      606/sshd: /usr/sbin 
tcp6       0      0 :::40419                :::*                    LISTEN      1035/promtail       
tcp6       0      0 :::10250                :::*                    LISTEN      608/k3s server      
tcp6       0      0 :::6443                 :::*                    LISTEN      608/k3s server      
tcp6       0      0 :::6767                 :::*                    LISTEN      576/sadagent       
```

3. check the status of the web pod

No web pod is running.

```
admin@i-056e412b0fa3fba26:~$ kubectl get pod -n web
NAME                                 READY   STATUS             RESTARTS   AGE
webapp-deployment-666b67994b-5sffz   0/1     Terminating        0          2y201d
webapp-deployment-666b67994b-ggw9s   0/1     ImagePullBackOff   0          10m
```

4. check why `ImagePullBackOff`

pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed

```
admin@i-056e412b0fa3fba26:~$ kubectl describe pod webapp-deployment-666b67994b-ggw9s -n web
  Type     Reason     Age                   From               Message
  ----     ------     ----                  ----               -------
  Normal   Scheduled  12m                   default-scheduler  Successfully assigned web/webapp-deployment-666b67994b-ggw9s to i-056e412b0fa3fba26
  Normal   Pulling    10m (x4 over 12m)     kubelet            Pulling image "webapp"
  Warning  Failed     10m (x4 over 12m)     kubelet            Failed to pull image "webapp": rpc error: code = Unknown desc = failed to pull and unpack image "docker.io/library/webapp:latest": failed to resolve reference "docker.io/library/webapp:latest": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
  Warning  Failed     10m (x4 over 12m)     kubelet            Error: ErrImagePull
  Warning  Failed     10m (x6 over 12m)     kubelet            Error: ImagePullBackOff
  Normal   BackOff    2m17s (x42 over 12m)  kubelet            Back-off pulling image "webapp"
```

5. run local docker registry

```
admin@i-056e412b0fa3fba26:~$ sudo docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
admin@i-056e412b0fa3fba26:~$ sudo docker run -d -p 5000:5000 --name registry registry:2
1e336cfbff408bcf4d62a4de1303bab51c413a2c55c1691ac562ca1b09a2a5fd
admin@i-056e412b0fa3fba26:~$ sudo docker ps
CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                       NAMES
1e336cfbff40   registry:2   "/entrypoint.sh /etc…"   5 seconds ago   Up 4 seconds   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   registry
```

6. push webapp image to local docker registry 

```
admin@i-056e412b0fa3fba26:~$ sudo docker tag webapp localhost:5000/webapp
admin@i-056e412b0fa3fba26:~$ sudo docker push localhost:5000/webapp
Using default tag: latest
The push refers to repository [localhost:5000/webapp]
d4a3f4c0cc92: Pushed 
2d08ca8d8c31: Pushed 
be0120f1f0a9: Pushed 
f1ec60f70b75: Pushed 
55fd06cb471b: Pushed 
b249887652be: Pushed 
95a02847aa85: Pushed 
b45078e74ec9: Pushed 
latest: digest: sha256:529296e183723c5170e832cac2c1144e3f11c15d33bee5900d88842df0232e35 size: 1995
admin@i-056e412b0fa3fba26:~$ curl http://localhost:5000/v2/_catalog
{"repositories":["webapp"]}
```

7. change the deployment manifest pull image from localhost:5000

```
admin@i-056e412b0fa3fba26:~$ cat deployment.yml | grep webapp
  name: webapp-deployment
      app: webapp
        app: webapp
      - name: webapp
        image: localhost:5000/webapp
admin@i-056e412b0fa3fba26:~$ kubectl apply -f deployment.yml 
deployment.apps/webapp-deployment configured
admin@i-056e412b0fa3fba26:~$ kubectl get pods -n web
NAME                                 READY   STATUS        RESTARTS   AGE
webapp-deployment-666b67994b-5sffz   0/1     Terminating   0          2y201d
webapp-deployment-5b98dcc989-jj578   1/1     Running       0          8s
```

8. allow k8s to configure node port 8888 by updating k3s unit file (its managed by systemd)

```
ExecStart=/usr/local/bin/k3s \
    server \
        '--write-kubeconfig-mode' \
        '644' \
        '--service-node-port-range' \
        '8888-32767' \
```

8. fix the nodeport

- change selector to `app: webapp`
- change nodeport to `8888`
