# Power Control

When the power button is pressed, the ESP loses power immediately. That is fine
for the microcontroller, but the Raspberry Pi host should be shut down cleanly
to avoid SD-card corruption.

The shutdown circuit drives GPIO4 high while power is present. When ESP power is
removed, GPIO4 drops low and the Pi starts shutdown. Supercaps provide a short
time window for Linux to complete shutdown.

<img src="./pics/orover messaging-supercap.png" width="600" /> 

## Enable / disable

Update `config.ini`. Under section `[scripts]` add:

```
powercontrol = powercontrol.py
```

The key name can be any descriptive string, but `powercontrol` is recommended.
After updating config, restart oRover.

To disable power control, remove (or comment out) the line in `[scripts]`.

## Parameters
Add section `[powercontrol]` if it does not exist.

The script accepts these parameters:

| Param | Description |
|-------|-------------|
|pin = X| GPIO pin where shutdown detection is connected (BCM numbering). Default: `4` |
|sleep_time = X| Seconds to wait after first low signal to filter glitches. Default: `2.0` |