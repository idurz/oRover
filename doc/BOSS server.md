# BOSS server

## Goal
The file boss.py implements a small central BOSS server that receives JSON messages from clients over ZMQ, validates them, dispatches to handlers, and replies back to the requester.

## Startup & configuration

Reads configuration and sets up logging using a FileHandler and JsonFormatter (from pythonjsonlogger.json). Next it creates a ZMQ Context() and a REP socket bound to the configured boss_socket. The socket send timeout is set from config.

## Main loop

main() logs "Started" then loops forever to call read_requests(). It sends the returned answer back with socket.send.

## Reading a request
Receives raw bytes with socket.recv(), decodes and parses JSON via json.loads.
Validates message fields and content; if a check fails, returns an error string (which main() will send back).

## Message structure and required fields
Messages are expected to contain fields defined in orover.KNOWN_FIELDS.
Typical fields used in code: id (UUID v4), ts (timestamp string), src (source/origin), prio (priority), reason (what the message is about), plus optional body.

## Validation steps
orover.all_fields_present(message, orover.KNOWN_FIELDS) — ensures required fields exist.
valid_uuid(message['id']) — checks id is a UUID v4.
valid_datetime(message['ts']) — checks ts parses with format %Y-%m-%dT%H:%M:%S.%f.
valid_source(message['src']) — intends to check src against known origins/controllers.
valid_priority(message['prio']) — intends to check priority membership.
If any validation fails, the function returns a descriptive discard string.
Dispatching

A DISPATCH dict maps reasons to handler functions, for example:
orover.event.object_detected -> handle_event_object_detected
orover.cmd.shutdown -> handle_cmd_shutdown
read_requests() looks up the handler by message['reason'] and calls it. If unknown, returns a discard message.
Handlers

handle_event_object_detected(message):
Extracts sensor name with orover.get_name(message.get('src')).
Requires distance in body; logs/prints a warning and returns "OK".
handle_cmd_shutdown(message):
Logs the shutdown reason, sends a b"Shutting down all systems" reply directly on socket, closes socket and terminates context, logs, and calls exit(0).
Note: because this handler calls exit(0) after sending, the normal reply-send in main() won't run for shutdown.
Logging

Uses logger.info(...) throughout; read_requests() logs handled requests with logger.info("Request handled", extra={"request": message, "result": result}).
Formatter is JSON-like when python-json-logger is available.

## Configuration items
Check the table in [config.md](./config_mapping.md)

