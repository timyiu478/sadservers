## "Chennai": Pull a Rabbit from a Hat

### Problem

https://sadservers.com/newserver/chennai

### Solution

1. check the `docker-compose.yml`

- 3 rabbitmq servers, 1 HAProxy
- Unknown: how rabbitMQ form/join a cluster?
- There are some config about user account and network configured by environment variables

```
  rabbitmq1:
    image: rabbitmq:3-management
    hostname: rabbitmq1
    environment:
      - RABBITMQ_DEFAULT_USER=${RABBITMQ_DEFAULT_USER}
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_DEFAULT_PASS}
      - RABBITMQ_DEFAULT_VHOST=${RABBITMQ_DEFAULT_VHOST}
```

2. check any defined `RABBITMQ_` environment variables

There is a `.env` file. Docker will automatically loads the `.env` file and substitutes the variables.

What is `VHOST`? It acts as a namespace to sperate resources such as queues.

```
admin@i-0ba1b861cf6c94dd1:~/rabbitmq-cluster-docker-master$ printenv | grep RABB
admin@i-0ba1b861cf6c94dd1:~/rabbitmq-cluster-docker-master$ cat .env
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_DEFAULT_VHOST=/
```

3. try `docker compose up` and see what will happen

```
rabbitmq-cluster-docker-master-rabbitmq1-1  | tail: cannot open '/var/log/rabbitmq/*.log' for reading: No such file or directory
rabbitmq-cluster-docker-master-rabbitmq1-1  | tail: no files remaining
```

```
rabbitmq-cluster-docker-master-rabbitmq3-1  | rabbit@rabbitmq1:
rabbitmq-cluster-docker-master-rabbitmq3-1  |   * unable to connect to epmd (port 4369) on rabbitmq1: nxdomain (non-existing domain)
```

4. check the file permissions

We only can modify the `cluster-entrypoint.sh`.

```
-rwxrwxrwx 1 admin            root   723 May 16  2022 cluster-entrypoint.sh
-rw-r--r-- 1 root             root  1399 May 16  2022 docker-compose.yml
-rw-r--r-- 1 root             root  1298 May 16  2022 haproxy.cfg
```

5. view the `cluster-entrypoint.sh`

```
#!/bin/bash

set -e

# Change .erlang.cookie permission
chmod 400 /var/lib/rabbitmq/.erlang.cookie

# Get hostname from enviromant variable
HOSTNAME=`env hostname`
echo "Starting RabbitMQ Server For host: " $HOSTNAME

if [ -z "$JOIN_CLUSTER_HOST" ]; then
    /usr/local/bin/docker-entrypoint.sh rabbitmq-server &
    sleep 5
    rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit\@$HOSTNAME.pid
else
    /usr/local/bin/docker-entrypoint.sh rabbitmq-server -detached
    sleep 5
    rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit\@$HOSTNAME.pid
    rabbitmqctl stop_app
    rabbitmqctl join_cluster rabbit@$JOIN_CLUSTER_HOST
    rabbitmqctl start_app
fi

# Keep foreground process active ...
tail -f /var/log/rabbitmq/*.log
```

6. the logs are outputted to `stdout` stream

But we can't update the rabbitmq log config because lack of write permission to `docker-compose.yml`

```
rabbitmq-cluster-docker-master-rabbitmq1-1  |   Logs: <stdout>
rabbitmq-cluster-docker-master-rabbitmq1-1  | 
rabbitmq-cluster-docker-master-rabbitmq1-1  |   Config file(s): /etc/rabbitmq/conf.d/10-defaults.conf
```

7. try to keep rabbitmq servers run by `sleep infinity` instead of watich the logs

```
# Keep foreground process active ...
# tail -f /var/log/rabbitmq/*.log
sleep infinity
```

8. try to publish message

```
admin@i-0967063683d408162:~$ python3 ~/producer.py hello-lwc
Traceback (most recent call last):
  File "/home/admin/producer.py", line 23, in <module>
    channel.queue_declare(queue=QUEUE)
  File "/usr/local/lib/python3.9/dist-packages/pika/adapters/blocking_connection.py", line 2512, in queue_declare
    validators.require_string(queue, 'queue')
  File "/usr/local/lib/python3.9/dist-packages/pika/validators.py", line 15, in require_string
    raise TypeError('%s must be a str or unicode str, but got %r' % (
TypeError: queue must be a str or unicode str, but got None
```

8. view the `producer.py`


Line 9:  QUEUE = os.getenv('RMQ_QUEUE')

```
admin@i-0967063683d408162:~$ cat -n producer.py 
     1  import pika
     2  import os
     3  import sys
     4
     5  # Auth port and queue from env vars
     6  USER = os.getenv('RMQ_USER', 'guest')
     7  PASSWORD = os.environ.get('RMQ_PASSWORD', 'guest')
     8  PORT = os.environ.get('RMQ_PORT', 5672)
     9  QUEUE = os.getenv('RMQ_QUEUE')
    10
    11  # message is the argument
    12  MESSAGE = sys.argv[1]
    13
    14  credentials = pika.PlainCredentials(USER, PASSWORD)
    15  parameters = pika.ConnectionParameters('localhost', PORT, '/', credentials)
    16
    17  # Establish a connection to RabbitMQ
    18  connection = pika.BlockingConnection(parameters)
    19
    20  channel = connection.channel()
    21
    22  # Declare a queue
    23  channel.queue_declare(queue=QUEUE)
    24
    25  # Publish a message to the queue
    26  channel.basic_publish(exchange='', routing_key=QUEUE, body=MESSAGE)
    27  print("Message sent to RabbitMQ")
    28
    29  # Close the connection
    30  connection.close()
```

9. set a env var `RMQ_QUEUE=test`

```
admin@i-0967063683d408162:~$ export RMQ_QUEUE=test
admin@i-0967063683d408162:~$ python3 ~/producer.py hello-lwc
Message sent to RabbitMQ
```

10. try to run `comsumer.py` to consume the message 

```
admin@i-0967063683d408162:~$ python3 ~/consumer.py
Traceback (most recent call last):
  File "/home/admin/consumer.py", line 14, in <module>
    connection = pika.BlockingConnection(parameters)
  File "/usr/local/lib/python3.9/dist-packages/pika/adapters/blocking_connection.py", line 360, in __init__
    self._impl = self._create_connection(parameters, _impl_class)
  File "/usr/local/lib/python3.9/dist-packages/pika/adapters/blocking_connection.py", line 451, in _create_connection
    raise self._reap_last_connection_workflow_error(error)
pika.exceptions.ProbableAuthenticationError: ConnectionClosedByBroker: (403) 'ACCESS_REFUSED - Login was refused using authentication mechanism PLAIN. For details see the broker logfile.'
```

11. view the `consumer.py`


```
admin@i-0967063683d408162:~$ cat -n consumer.py 
     1  import pika
     2
     3  # variables
     4  USER = 'username'
     5  PASSWORD = 'password'
     6  PORT = 5672
     7  QUEUE = 'hello'
     8
     9  # Connection parameters
    10  credentials = pika.PlainCredentials(USER, PASSWORD)
    11  parameters = pika.ConnectionParameters('localhost', PORT, '/', credentials)
    12
    13  # Establish a connection to RabbitMQ
    14  connection = pika.BlockingConnection(parameters)
    15  channel = connection.channel()
    16
    17  # Declare a queue
    18  channel.queue_declare(queue=QUEUE)
    19
    20  # Fetch a single message from the queue
    21  method_frame, header_frame, body = channel.basic_get(queue='hello', auto_ack=True)
    22
    23  if method_frame:
    24      # Print the received message
    25      print(body.decode())
    26  else:
    27      print("No messages in the queue")
    28
    29  # Close the connection
    30  connection.close()
```

12. Requirement: Do not change the consumer.py and producer.py files

It means we have to follow the setting defined in `consumer.py` such as queue and user credential.

```
     4  USER = 'username'
     5  PASSWORD = 'password'
     6  PORT = 5672
     7  QUEUE = 'hello'
```

13. add new user `username` to rabbitmq server

```
admin@i-0967063683d408162:~/rabbitmq-cluster-docker-master$ cat cluster-entrypoint.sh 
if [ -z "$JOIN_CLUSTER_HOST" ]; then
    /usr/local/bin/docker-entrypoint.sh rabbitmq-server &
    sleep 5
    rabbitmqctl wait /var/lib/rabbitmq/mnesia/rabbit\@$HOSTNAME.pid
    rabbitmqctl add_user username password
    rabbitmqctl set_permissions -p / username ".*" ".*" ".*"
```

14. set correct environmental variables

```
admin@i-0967063683d408162:~/rabbitmq-cluster-docker-master$ export RMQ_QUEUE=hello RMQ_USER=username RMQ_PASSWORD=password
```
