## "Bilbao": Basic Kubernetes Problems

### Problem

> There's a Kubernetes Deployment with an Nginx pod and a Load Balancer declared in the manifest.yml file. The pod is not coming up. Fix it so that you can access the Nginx container through the Load Balancer.

https://sadservers.com/scenario/bilbao

### Solution

1. get some information about the nginx pod

```
admin@i-0b257935f65e736ba:~$ kubectl get pods 
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-67699598cc-zrj6f   0/1     Pending   0          436d
```

```
admin@i-0b257935f65e736ba:~$ kubectl describe pods nginx-deployment-67699598cc-zrj6f
Name:             nginx-deployment-67699598cc-zrj6f
Namespace:        default
Priority:         0
Service Account:  default
Node:             <none>
Labels:           app=nginx
                  pod-template-hash=67699598cc
Annotations:      <none>
Status:           Pending
IP:               
IPs:              <none>
Controlled By:    ReplicaSet/nginx-deployment-67699598cc
Containers:
  nginx:
    Image:      localhost:5000/nginx
    Port:       80/TCP
    Host Port:  0/TCP
    Limits:
      cpu:     100m
      memory:  2000Mi
    Requests:
      cpu:        100m
      memory:     2000Mi
    Environment:  <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-mslhc (ro)
Conditions:
  Type           Status
  PodScheduled   False 
Volumes:
  kube-api-access-mslhc:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   Guaranteed
Node-Selectors:              disk=ssd
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  436d  default-scheduler  0/2 nodes are available: 1 node(s) didn't match Pod's node affinity/selector, 1 node(s) had untolerated taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available: 2 Preemption is not helpful for scheduling..
  Warning  FailedScheduling  118s  default-scheduler  0/2 nodes are available: 1 node(s) didn't match Pod's node affinity/selector, 1 node(s) had untolerated taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available: 2 Preemption is not helpful for scheduling..
```

2. based on the `manifest.yml`, the deployment is selecting the node with label `disk: ssd`

```
      nodeSelector:
        disk: ssd
```

3. check the node status and their labels

```
admin@i-0b257935f65e736ba:~$ kubectl get nodes --show-labels
NAME                  STATUS     ROLES                  AGE    VERSION        LABELS
i-02f8e6680f7d5e616   NotReady   control-plane,master   436d   v1.28.5+k3s1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=k3s,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=i-02f8e6680f7d5e616,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=true,node-role.kubernetes.io/master=true,node.kubernetes.io/instance-type=k3s
node1                 Ready      control-plane,master   436d   v1.28.5+k3s1   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=k3s,beta.kubernetes.io/os=linux,kubernetes.io/arch=amd64,kubernetes.io/hostname=node1,kubernetes.io/os=linux,node-role.kubernetes.io/control-plane=true,node-role.kubernetes.io/master=true,node.kubernetes.io/instance-type=k3s
admin@i-0b257935f65e736ba:~$ kubectl get nodes --show-labels | grep ssd
```

4. assign `disk: ssd` label to the ready node `node1` or remove the node selector in the `manifest.yml`

```
admin@i-0b257935f65e736ba:~$ kubectl label nodes node1 disk=ssd
node/node1 labeled
```

5. check the pod status and it shows `insufficient memory`

```
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: "2025-03-29T07:24:52Z"
      message: '0/2 nodes are available: 1 Insufficient memory, 1 node(s) had untolerated
        taint {node.kubernetes.io/unreachable: }. preemption: 0/2 nodes are available:
        1 No preemption victims found for incoming pod, 1 Preemption is not helpful
        for scheduling..'
      reason: Unschedulable
```

6. check the node memory capacity

```
Addresses:
  InternalIP:  10.0.0.245
  Hostname:    node1
Capacity:
  cpu:                2
  ephemeral-storage:  8026128Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
Allocatable:
  cpu:                2
  ephemeral-storage:  7807817313
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             2000036Ki
  pods:               110
```

7. reduce the nginx memory limits and requests

```diff
        resources:
          limits:
            memory: 2000Mi
          requests:
            memory: 2000Mi
---
        resources:
          limits:
            memory: 1000Mi
          requests:
            memory: 1000Mi
```

Its running

```
admin@i-0b257935f65e736ba:~$ kubectl get pods
NAME                                READY   STATUS              RESTARTS   AGE
nginx-deployment-67699598cc-xzp6r   0/1     Pending             0          6m30s
nginx-deployment-794f87f659-wgql6   0/1     ContainerCreating   0          6s
admin@i-0b257935f65e736ba:~$ kubectl get pods -w
NAME                                READY   STATUS    RESTARTS   AGE
nginx-deployment-794f87f659-wgql6   1/1     Running   0          11s
```


