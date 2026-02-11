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
      ,"me"  : 'me'  sys.argv[0]
      ,"host": 'hostname'  os.uname().nodename
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


## Publishing messages

how to

## Subscribing to messages

how to
