# Enum Name Uniqueness Test

## Goal
`pi/test/test_enum_name_uniqueness.py` is a regression guard that detects
duplicate member names across enum classes in `oroverlib.py`.

This prevents ambiguous name-based enum lookup issues, such as handler
registration mismatches when two enum classes share the same member name.

## Why this test exists
The shutdown issue showed that generic name-to-enum lookup can resolve to the
wrong enum class when names are reused.

Example risk:
- handler method name maps to `"shutdown"`
- lookup picks the wrong enum class member
- dispatch key does not match incoming message reason
- valid messages are discarded with "no handler" logs

## What it checks
The test:
1. Loads all `IntEnum` classes defined in `oroverlib.py`
2. Collects all member names across those classes
3. Fails when a member name appears in more than one enum class

## How to run
From the `pi` directory:

```bash
python3 test/test_enum_name_uniqueness.py
```

## Exit codes
- `0`: No duplicate enum member names found
- `1`: One or more duplicate enum member names found

## Example failure output
```text
FAIL: duplicate enum member names detected
  - test_message: event, origin
Hint: make member names unique across enum classes or use typed lookup logic.
```

## Recommended follow-up on failure
- Prefer unique enum member names across classes, or
- Avoid generic name-to-enum lookup for handler registration and use typed
  lookup based on handler prefix (`cmd_`, `state_`, `event_`).
