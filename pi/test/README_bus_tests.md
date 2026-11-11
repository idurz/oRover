# Reusable Bus Integration Tests

These tests validate process behavior over the ZeroMQ event bus using a shared
reusable test library in `bus_testlib.py`.

## Design goals
- Reusable scenario helpers (`BusProbe`, `Expectation`, `run_scenario`)
- Process-specific tests with small scenario definitions
- Observable outcomes only (bus event or process exit)

## Test programs
- `boss_test.py`
  - Publishes `state.battery`
  - Expects `event.lowBattery` from `boss.py`

- `ugv_test.py`
  - Publishes `cmd.set_motor_speed`
  - Expects feedback topic from `ugv.py` (default `state.actuator_speed`)
  - Topic/source filters are configurable for reuse

- `app_test.py`
  - Calls `POST /control` on `app.py`
  - Expects `cmd.set_motor_speed` on the bus

- `stop_test.py`
  - Executes `stop.py`
  - Expects `cmd.shutdown` on the bus from `orover_stopper`

- `launcher_test.py`
  - Starts `launcher.py` with temporary minimal config
  - Publishes `cmd.shutdown`
  - Expects launcher process exit

## Run examples
From `pi/test`:

```bash
export PATH="$(cd .. && pwd)/.venv/bin:$PATH"
export PYTHONPATH="$(cd .. && pwd)${PYTHONPATH:+:$PYTHONPATH}"
python3 boss_test.py
python3 ugv_test.py
python3 app_test.py --url http://localhost:5000/control --action stop
python3 stop_test.py
python3 launcher_test.py
```

These commands default to `/etc/orover/config.ini`. Use `--config <path>` to select another file.

## Notes
- Tests assume `eventbus.py` is running and reachable via config endpoints.
- Some tests require the target process to already be running (`boss.py`, `ugv.py`, `app.py`).
- `hcsr04.py` is hardware-triggered (GPIO) and is not covered by command-driven bus tests.

## Installer And Serial Error Tests
From the repository root, run the hardware-free checks:

```bash
bash pi/test/install_test.sh
python3 -m unittest discover -s pi/test -p test_ugv_serial_errors.py -v
```

The installer test mocks system commands; the serial-error test simulates port failures. Neither verifies Raspberry Pi hardware or systemd behavior.
