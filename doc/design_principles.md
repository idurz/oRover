
# Design Principles

![Diagram](./pics/orover%20messaging.drawio.png)

oRover is build on a distributed system where senors, actuars, motors and analyzers work together by sending messages via the [zeromq](https://zeromq.org/) request/reply format.
The [BOSS server](./BOSS_server.md) is the central heart of the oRover system. It runs in the background continous, accepts requests and status updates and makes decisions to control motors
and actuars based on that.

By using [zeromq](https://zeromq.org/) and a standarized message format between all elements the system is futureproof and easily adaptable for other type of sensors, image analyzers etc. Converting the message to specific hardware or software needs is done in separate modules which makes troubleshooting easier.

## Client to BOSS messages

Lets start with an example. The hcsr04 is an ultrasound detector which returns a distance signal. Suppose you want to use that sensor and send the distance info to BOSS. Based on that info BOSS could e.g. decide to change direction.

* The hcsr04 sensor opens the communication to BOSS using the library function:
`socket = orover.connect_to_server()`

* Next it reads the distance: `distance = measure_distance(echopin,triggerpin)`

* Now it is time to inform BOSS. You need to send a message containing
  * the source "src", which tells BOSS which sensor has read the distance
  * the reason "reason", which tells BOSS what happened
  * the body containing "distance" which is the value read from the sensor.
* You need to use enumerate values from the [orover_lib](../pi/orover_lib.py) for src and reason.
* Use the `orover.send` function with parameters `(socket
                                    ,src = orover.origin.sensor_ultrasonic_front 
                                    ,reason = orover.event.object_detected
                                    ,body = {"distance": distance})`
* Priority (parameter prio) is optional and is default Normal. To switch to high, or low
add the corresping priority enum from the [orover_lib](../pi/orover_lib.py).
* The send function adds guid, timestamp, processid, python filename, hostname and
priority (prio) to the message, converts it to json and sends it to BOSS.
* The send function always retuns an answer since it is a request/reply system
* The answer is a text string.


* BOSS receives the request, does type checking and dispatches a function which 
belongs to the reason. See [handlers](./reason_info.md) for details on workings 
for the events, allowed parameters possible answers.

