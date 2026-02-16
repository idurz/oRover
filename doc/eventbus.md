# eventbus

## Why an eventbus

Each part of the system has to communicate with other parts. Since we want to keep the system flexible where add-ons or additional features must be easy to create, a simple message structure is important. If there is no message bus, scripts needs to know of each other because a message channel needs to be opened. This might end up with several cross-linked message channels. 

By introducing a bus system, all other components just have to know about the bus. A component opens a pub/sub channel to the bus and can start sending messages. The bus reads messages and passed them tru to all who are interested.

```
+------+                 +-----------+                   +-----+
|sensor| --> publish --> |eventbus.py| <-- subscribe <-- |actor|
+------+                 +-----------+                   +-----+
```

## Message format
Each message send to and passed from the bridge will have the same format. Use the [JSON](https://www.json.org/json-en.html) format.

```
msg = {"id"  : 'guid'
      ,"ts"  : 'datetime' datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
      ,"src" : 'src'
      ,"me"  : 'me' 
      ,"host": 'hostname'  
      ,"prio": 'prio'
      ,"reason": 'reason'
      ,"body":  {}
     }
```

| Parameter | Type      | Description |
|-----------|-----------|-------------|
| id        | Automatic | An unique id (GUID) of type uuid4. If you use the default orover.send function, this field is automaticly added. You can also use `str(uuid.uuid4())` |
| ts        | Automatic |Date and time in the format YYYY-MM-DDTHH:MM:SS. If you use the default orover.send function, this field is automaticly added. You can also use `datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')` |
| me        | Automatic | Name of the sending script. If you use the default orover.send function, this field is automaticly added. You can also use `sys.argv[0]` |
| host      | Automatic | Tells the system on which system this script resides. If you use the default orover.send function, this field is automaticly added. You can also use `os.uname().nodename` |
| prio      | Optional  | Priority of the message. Defaults to normal. If you use the default orover.send function, this field is automaticly added. Use the [enumeration](enumeration) format from the **priority** list . Example `"src" : orover.priority.high` |
| body      | Optional | The body field contains parameters and is dependant on the source (src) and reason for the message. Check the (boss controler)[boss_server.md] for specific details on the message type you want to sent. Parameters are in json format. Example `{"distance" : "20.0"}` |
| src       | Mandatory | Tells the system who is sending the message. Use the [enumeration](enumeration format from the **origin or controller ** list. Example `orover.controller.remote_interface` |
| reason    | Mandatory | Tells the system what the reason is for sending the message. What happened, or what is your demmand? Use the [enumeration](enumeration format from the **cmd, state or event** list. Example `orover.cmd.moveTo` |

## Eventbus working

The Pub/Sub pattern is great for multiple subscribers and a single publisher, but if you need multiple publishers then the XPub/XSub pattern will be of interest. We need XPUB and XSUB sockets because ZeroMQ does subscription forwarding from subscribers to publishers. XSUB and XPUB are exactly like SUB and PUB except they expose subscriptions as special messages. The proxy has to forward these subscription messages from subscriber side to publisher side, by reading them from the XSUB socket and writing them to the XPUB socket. This is the main use case for XSUB and XPUB.

It can be seen that the PublisherSocket connnects to the XSubscriberSocket address. The intermediary is responsible for relaying the messages bidirectionally between the XPublisherSocket and the XSubscriberSocket. NetMQ provides a Proxy class which makes this simple. It can be seen that the SubscriberSocket connects to the XPublisherSocket address.

This results in the following example code:

```
# Create context
ctx = zmq.Context()

# Bind to subscriber port
xsub = ctx.socket(zmq.XSUB)
xsub.bind("tcp://*:5556")

# Reuse context and bind to publissher port
xpub = ctx.socket(zmq.XPUB)
xpub.bind("tcp://*:5555")

# Some info
print("Event bus running:")
print("  publishers -> tcp://*:5556")
print("  subscribers -> tcp://*:5555")

# Start the proxy class to forward messages
zmq.proxy(xsub, xpub)
```

## Client publishing messages

You can use the following example code for a client who wants to send messages. A message consists of a topic word, a space, and other text.


```
ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5555")

# important: allow 1 second sleep to settle for publisher
time.sleep(1)
a = "topic string"
pub.send_string(a)
```

## Client subscribing to messages

You can use the following example code for a client receiving messsages. A message consists of a topic word, a space and other text.

```
ctx = zmq.Context()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://localhost:5555")
sock.setsockopt_string(zmq.SUBSCRIBE, "")

while True:
    msg = sock.recv_string()
    print(f"DEBUG receiver: {msg}")
```