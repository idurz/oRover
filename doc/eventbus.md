# eventbus

## Why an eventbus
oRover components communicate through a shared ZeroMQ message bus. This keeps
components loosely coupled: each process only needs to know bus endpoints, not
all peer process addresses.

```
+-----------+     publish      +-----------+     subscribe     +-----------+
| producer  | ---------------> | eventbus  | --------------->  | consumer   |
+-----------+                  +-----------+                   +-----------+
```

## Message format
Messages are sent as `topic + space + JSON payload`.

Example payload:

```json
{
  "id": "uuid4",
  "ts": "2026-04-08T12:34:56.123456",
  "src": 3000,
  "me": "hcsr04",
  "host": "robot",
  "prio": 5,
  "reason": 6402,
  "body": {}
}
```

Key fields:
- `id`: unique message id (UUID)
- `ts`: timestamp (`%Y-%m-%dT%H:%M:%S.%f`)
- `src`: source enum value (`origin`, `actuator`, or `controller`)
- `prio`: priority enum value
- `reason`: command/state/event enum value
- `body`: message-specific JSON object

See [enumeration.md](enumeration.md) for enum definitions.

## Endpoints (from config.ini)
The default endpoint roles are:

| Config key | Default | Used by |
|---|---|---|
| `client_pub_socket` | `tcp://localhost:5556` | client publishers |
| `client_sub_socket` | `tcp://localhost:5555` | client subscribers |
| `bus_xsub_socket` | `tcp://localhost:5556` | eventbus XSUB connect target |
| `bus_xpub_socket` | `tcp://*:5555` | eventbus XPUB bind target |

## Eventbus internals
The bus process uses an XSUB/XPUB proxy (`zmq.proxy`) to forward messages.
In the current implementation:
- XSUB connects to `bus_xsub_socket` and also binds `tcp://*:5556`
- XPUB binds to `bus_xpub_socket`

## Client examples
Publisher:

```python
import time
import zmq

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://localhost:5556")

time.sleep(1.0)  # allow subscriber subscriptions to propagate
pub.send_string("test.topic hello")
```

Subscriber:

```python
import zmq

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5555")
sub.setsockopt_string(zmq.SUBSCRIBE, "test.topic")

while True:
    print(sub.recv_string())
```

## Handler convention in bus clients
Most oRover bus clients inherit `baseprocess` and use method naming conventions
for handler registration:
- `event_<name>`
- `cmd_<name>`
- `state_<name>`

See [boss_server.md](boss_server.md) for details.
