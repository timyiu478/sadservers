## "Bengaluru": Kubernetes StatefulSet least known characteristic

### Problem

> Make the StatefulSet pod demo-statefulset-0 run on the available node.

https://sadservers.com/scenario/bengaluru

### Solution

1. check the statefulset manifest

```
admin@i-03523af80c1339408:~$ kubectl get statefulset -o yaml
apiVersion: v1
items:
- apiVersion: apps/v1
  kind: StatefulSet
  metadata:
    annotations:
      kubectl.kubernetes.io/last-applied-configuration: |
        {"apiVersion":"apps/v1","kind":"StatefulSet","metadata":{"annotations":{},"name":"demo-statefulset","namespace":"default"},"spec":{"replicas":1,"selector":{"matchLabels":{"app":"demo-sts"}},"serviceName":"demo-service","template":{"metadata":{"labels":{"app":"demo-sts"}},"spec":{"affinity":{"nodeAffinity":{"preferredDuringSchedulingIgnoredDuringExecution":[{"preference":{"matchExpressions":[{"key":"kubernetes.io/hostname","operator":"In","values":["k3d-mycluster-agent-0"]}]},"weight":90},{"preference":{"matchExpressions":[{"key":"kubernetes.io/hostname","operator":"In","values":["k3d-mycluster-agent-1"]}]},"weight":10}]}},"containers":[{"command":["/bin/sh","-c","sleep infinity"],"image":"alpine:3.21","name":"demo-container","resources":{"limits":{"cpu":"100m","memory":"128Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}}],"tolerations":[{"effect":"NoExecute","key":"node.kubernetes.io/unreachable","operator":"Exists","tolerationSeconds":30},{"effect":"NoExecute","key":"node.kubernetes.io/not-ready","operator":"Exists","tolerationSeconds":30}]}}}}
    creationTimestamp: "2025-02-10T19:43:52Z"
    generation: 1
    name: demo-statefulset
    namespace: default
    resourceVersion: "1407"
    uid: 298fc60a-e3d5-4924-8654-5642a3a923bd
  spec:
    persistentVolumeClaimRetentionPolicy:
      whenDeleted: Retain
      whenScaled: Retain
    podManagementPolicy: OrderedReady
    replicas: 1
    revisionHistoryLimit: 10
    selector:
      matchLabels:
        app: demo-sts
    serviceName: demo-service
    template:
      metadata:
        creationTimestamp: null
        labels:
          app: demo-sts
      spec:
        affinity:
          nodeAffinity:
            preferredDuringSchedulingIgnoredDuringExecution:
            - preference:
                matchExpressions:
                - key: kubernetes.io/hostname
                  operator: In
                  values:
                  - k3d-mycluster-agent-0
              weight: 90
            - preference:
                matchExpressions:
                - key: kubernetes.io/hostname
                  operator: In
                  values:
                  - k3d-mycluster-agent-1
              weight: 10
        containers:
        - command:
          - /bin/sh
          - -c
          - sleep infinity
          image: alpine:3.21
          imagePullPolicy: IfNotPresent
          name: demo-container
          resources:
            limits:
              cpu: 100m
              memory: 128Mi
            requests:
              cpu: 50m
              memory: 64Mi
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        schedulerName: default-scheduler
        securityContext: {}
        terminationGracePeriodSeconds: 30
        tolerations:
        - effect: NoExecute
          key: node.kubernetes.io/unreachable
          operator: Exists
          tolerationSeconds: 30
        - effect: NoExecute
          key: node.kubernetes.io/not-ready
          operator: Exists
          tolerationSeconds: 30
    updateStrategy:
      rollingUpdate:
        partition: 0
      type: RollingUpdate
  status:
    availableReplicas: 0
    collisionCount: 0
    currentRevision: demo-statefulset-86f687bff9
    observedGeneration: 1
    replicas: 1
    updateRevision: demo-statefulset-86f687bff9
kind: List
metadata:
  resourceVersion: ""
```

2. force delete the replica pod

why? 

1. StatefulSet ensures that, at any time, there is at most one Pod with a given identity running in a cluster.
1. The statefulSet controller keeps waiting kubelet in stopped worker node `k3d-mycluster-agent-0`.
1. Force deletions do not wait for confirmation from the kubelet that the Pod has been terminated.

```
admin@i-01d10d30a8d0348cf:~$ kubectl delete pods demo-statefulset-0 --grace-period=0 --force
Warning: Immediate deletion does not wait for confirmation that the running resource has been terminated. The resource may continue to run on the cluster indefinitely.
pod "demo-statefulset-0" force deleted
admin@i-01d10d30a8d0348cf:~$ kubectl get pods
NAME                              READY   STATUS        RESTARTS      AGE
demo-deployment-578d68758-lcznf   1/1     Terminating   1 (13m ago)   47d
demo-deployment-578d68758-lj2bk   1/1     Running       0             11m
demo-statefulset-0                1/1     Running       0             24s
```
