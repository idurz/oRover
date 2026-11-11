# Systemd service
The [installer](../install.sh) creates and enables `orover.service` automatically. It runs the launcher in the foreground as the installing user, from the `pi/` directory, using the isolated virtual environment in `pi/.venv`. The environment uses the system's Raspberry Pi GPIO modules without exposing other system Python packages. It does not start the service immediately; it will start on the next boot.

Before starting, review `/etc/orover/config.ini`, including the serial port, GPIO pins and `[scripts]`. Existing system configuration is preserved on reinstall; when it does not exist, the installer migrates an existing `pi/config.ini` or copies the example. New configuration files are owned by root and readable by the installing user's primary group (mode `0640`); edit them with `sudo`. The installer adds the service user to `dialout` when available, which normally grants access to the serial device. Restart an already running service after changing group membership; log out and back in for interactive commands. The service user also needs GPIO access (on Raspberry Pi OS, the `gpio` group is commonly required). If `python_exec` is customized in the configuration, it must point to a Python interpreter with the same dependencies; the default `python3` uses the virtual environment.

When the configured serial port is `/dev/serial0`, the installer uses `raspi-config` to disable serial login and enable the UART. This removes serial-console login access and may require a reboot; the installer does not reboot automatically. If `raspi-config` is unavailable, configure the serial hardware and console manually. After reboot, verify access with `ls -lL /dev/serial0`; nonstandard device groups, permissions, or independently configured serial consoles may still need manual attention. Other configured serial ports do not trigger Raspberry Pi UART changes.

```bash
sudo systemctl start orover
sudo systemctl status orover
sudo systemctl stop orover
journalctl -u orover -f
```

To prevent automatic startup, run `sudo systemctl disable orover`. To update, rerun `bash install.sh [install-directory]`; the checkout must be able to fast-forward.