## "Buenos Aires": Kubernetes Pod Crashing 

### Problem

> There are two pods: "logger" and "logshipper" living in the default namespace. Unfortunately, logshipper has an issue (crashlooping) and is forbidden to see what logger is trying to say. Could you help fix Logshipper?

https://sadservers.com/scenario/buenos-aires

### Solution

1. get the pod names

```
admin@i-092290637700fc81f:~$ sudo kubectl get pods
NAME                          READY   STATUS    RESTARTS       AGE
logshipper-597f84bf4f-6ssjq   1/1     Running   5 (355d ago)   355d
logger-6f7fb76c9f-4jk77       1/1     Running   1 (110s ago)   355d
```

2. check the pod logs

```
admin@i-092290637700fc81f:~$ sudo kubectl logs logshipper-597f84bf4f-6ssjq
Exception when calling CoreV1Api->read_namespaced_pod_log: (403)
Reason: Forbidden
HTTP response headers: HTTPHeaderDict({'Audit-Id': 'a4933c4a-34cb-491b-9520-9f7aa83a3ce9', 'Cache-Control': 'no-cache, private', 'Content-Type': 'application/json', 'X-Content-Type-Options': 'nosniff', 'Date': 'Sun, 30 Mar 2025 09:54:53 GMT', 'Content-Length': '352'})
HTTP response body: {"kind":"Status","apiVersion":"v1","metadata":{},"status":"Failure","message":"pods \"logger-6f7fb76c9f-4jk77\" is forbidden: User \"system:serviceaccount:default:logshipper-sa\" cannot get resource \"pods/log\" in API group \"\" in the namespace \"default\"","reason":"Forbidden","details":{"name":"logger-6f7fb76c9f-4jk77","kind":"pods"},"code":403}



admin@i-092290637700fc81f:~$ sudo kubectl logs logger-6f7fb76c9f-4jk77
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
Hi, My brother logshipper cannot see what I am saying. Can you fix him?
```

3. check the log shipper k8s spec

```
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      app: logshipper
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: logshipper
    spec:
      containers:
      - command:
        - /usr/bin/python3
        - logshipper.py
        image: logshipper:v3
        imagePullPolicy: Never
        name: logshipper
        resources: {}
        securityContext:
          allowPrivilegeEscalation: true
          runAsGroup: 0
          runAsUser: 0
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      serviceAccount: logshipper-sa
      serviceAccountName: logshipper-sa
      terminationGracePeriodSeconds: 30
```

4. check `logshipper-sa` service account

```
admin@i-092290637700fc81f:~$ sudo kubectl get serviceaccount logshipper-sa -o yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"logshipper-sa","namespace":"default"}}
  creationTimestamp: "2024-04-08T17:47:13Z"
  name: logshipper-sa
  namespace: default
  resourceVersion: "1276"
  uid: caf2eab9-52f3-4f15-bf2e-b8c86e5e1671
```

5. create pod log reader role

```
admin@i-092290637700fc81f:~$ sudo kubectl apply -f pod-log-read-role.yaml 
role.rbac.authorization.k8s.io/pod-log-reader created
admin@i-092290637700fc81f:~$ cat pod-log-read-role.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-log-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

6. bind this pod log reader role to `logshipper-sa`

```
admin@i-092290637700fc81f:~$ sudo kubectl apply -f pod-log-read-rb.yaml 
rolebinding.rbac.authorization.k8s.io/pod-log-reader-binding created
admin@i-092290637700fc81f:~$ cat pod-log-read-rb.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-log-reader-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: logshipper-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-log-reader
  apiGroup: "rbac.authorization.k8s.io"
```

7. check service account "logshipper-sa" of "default" namespace can get pods in namespace "default"

```
admin@i-092290637700fc81f:~$ sudo kubectl auth can-i get pods/log/ --as=system:serviceaccount:default:logshipper-sa -n default
yes
```

8. found there are cluster role and cluster role binding for logshipper

```
admin@i-0878c3c24787655a6:~$ sudo kubectl get clusterrolebinding logshipper-cluster-role-binding -o yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRoleBinding","metadata":{"annotations":{},"name":"logshipper-cluster-role-binding"},"roleRef":{"apiGroup":"rbac.authorization.k8s.io","kind":"ClusterRole","name":"logshipper-cluster-role"},"subjects":[{"kind":"ServiceAccount","name":"logshipper-sa","namespace":"default"}]}
  creationTimestamp: "2024-04-08T17:47:13Z"
  name: logshipper-cluster-role-binding
  resourceVersion: "1275"
  uid: fc9ffc88-ae6c-47d6-bb9c-a5ec6e59bde4
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: logshipper-cluster-role
subjects:
- kind: ServiceAccount
  name: logshipper-sa
  namespace: default
```

```
admin@i-0878c3c24787655ar:~$ sudo kubectl get clusterrole logshipper-cluster-role -o yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    descripton: Think about what verbs you need to add.
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"rbac.authorization.k8s.io/v1","kind":"ClusterRole","metadata":{"annotations":{"descripton":"Think about what verbs you need to add."},"name":"logshipper-cluster-role"},"rules":[{"apiGroups":[""],"resources":["namespaces","pods","pods/log"],"verbs":["list"]}]}
  creationTimestamp: "2024-04-08T17:47:13Z"
  name: logshipper-cluster-role
  resourceVersion: "1274"
  uid: 6ef0ef3c-ad24-4469-a7b0-541a010b0d93
rules:
- apiGroups:
  - ""
  resources:
  - namespaces
  - pods
  - pods/log
  verbs:
  - list
```

9. add the verb `get` in logshipper-cluster-role and restart the logshipper pod

```
admin@i-0878c3c24787655a6:~$ sudo kubectl delete pod logshipper-597f84bf4f-6ssjq 
pod "logshipper-597f84bf4f-6ssjq" deleted
admin@i-0878c3c24787655a6:~$ sudo kubectl get pods
NAME                          READY   STATUS    RESTARTS      AGE
logger-6f7fb76c9f-4jk77       1/1     Running   1 (10m ago)   355d
logshipper-597f84bf4f-jrj8t   1/1     Running   0             4s
```
