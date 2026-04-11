# logserver

## Description
The logserver is a mandatory background process that collects log records from all oRover
processes via a socket-based logging handler and writes them to disk.

All processes send log records over TCP to logserver, which centralizes logging into
a single timestamped file. This makes troubleshooting easier by providing a unified
view of all process activity.

## How it works

1. On startup, logserver creates a `logs/` directory (configurable via `logdir` in config.ini)
2. A new log file is created with a timestamp: `orover_YYYYMMDDHHMMSS.log`
3. Logserver listens on `localhost:DEFAULT_TCP_LOGGING_PORT` (typically 9020)
4. All other oRover processes connect and send pickled LogRecord objects
5. Each record is unpickled and passed to the appropriate logger handler
6. Records are formatted and written to the current log file
7. On shutdown, old log files are automatically cleaned up (keeps last N files, default 10)

## Configuration parameters

Parameters are specified in the `[orover]` section of `config.ini`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| logdir | logs | Directory where log files are stored |
| logfile | orover.log | Log file basename; timestamp is appended automatically to create unique files |
| max_logfiles | 10 | Maximum number of log files to keep; older files are automatically deleted |
| logformat | %(asctime)s %(name)-8s %(levelname)-9s guid=%(guid)s %(message)s | Format string for log output |
| logdatefmt | %Y-%m-%d %H:%M:%S | Date format used in log timestamps |
| loglevel | DEBUG | Minimum log level to record (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

Example:
```
[orover]
logdir = logs
logfile = orover.log
max_logfiles = 10
loglevel = DEBUG
logformat = %(asctime)s %(name)-8s %(levelname)-9s guid=%(guid)s %(message)s
logdatefmt = %Y-%m-%d %H:%M:%S
```

## Structured logging and message correlation

Every log record includes a `guid` field that can be used to correlate logs across
processes for a single message flow:

- **Initial log capture**: When a process calls `send_event()`, it generates a UUID
  and sets the logging context to that UUID. All logs during event construction carry
  that guid.
  
- **Message handling**: When a process receives a message via `handle_message()`, the
  logging context is set to the incoming message's id. All logs during the handling
  of that message carry the same guid.
  
- **Default guid**: Logs not associated with a message show `guid=-`.

### Example

A single motion command flow across processes:

```
2026-04-11 14:23:45 boss       INFO     guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Sending move command
2026-04-11 14:23:45 boss       DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Preparing to send event
2026-04-11 14:23:45 ugv        DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Message received
2026-04-11 14:23:45 ugv        DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Validated message
2026-04-11 14:23:45 ugv        INFO     guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Setting motor speed to 50
2026-04-11 14:23:46 ugv        DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Motor response received
2026-04-11 14:23:46 boss       DEBUG    guid=a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6 Motion complete
```

All logs can be filtered by guid to see the complete flow of a single command.

## Log file rotation

Logserver automatically manages log files to prevent unbounded disk usage:

1. Each time logserver starts, a new timestamped log file is created
2. On startup, all log files matching the basename are scanned
3. If more than `max_logfiles` exist, the oldest ones are deleted
4. Only the most recent N log files are retained

Example directory structure after several restarts:
```
logs/
  orover_20260410121530.log
  orover_20260410150000.log
  orover_20260411092345.log   <- current
```

If `max_logfiles=3`, only the last three files are kept; older ones are deleted on startup.

## Troubleshooting

### Logs not appearing
- Check that logserver process is running: `ps aux | grep logserver`
- Verify logdir exists and is writable: `ls -la logs/`
- Check system logs for socket binding errors

### Disk space issues
- Increase `max_logfiles` (currently keeping more history means more disk usage)
- Or decrease `max_logfiles` to keep fewer log files
- Check individual log file sizes; very large files may indicate a logging loop

### Missing guid correlation
- Not all logs will have guids; only logs generated during message send/receive have guids
- Independent background processes may show `guid=-`
- This is normal

## See also
- [configuration.md](configuration.md) - Configuration parameters
- [technical documentation.md](technical%20documentation.md) - System architecture overview
