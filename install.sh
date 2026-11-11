#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${OROVER_REPO_URL:-https://github.com/idurz/oRover.git}"
INSTALL_DIR="${1:-$HOME/oRover}"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    printf '%s\n' \
        'Usage: bash install.sh [install-directory]' \
        '' \
        'Install or update oRover on a Debian-based Raspberry Pi with systemd.' \
        'Run as the user that should run the service, not as root; sudo is required.' \
        '' \
        'The installer:' \
        '  1. Installs Git, Python, venv, and Raspberry Pi GPIO if missing.' \
        '  2. Clones the repository or fast-forwards an existing checkout.' \
        '  3. Creates /etc/orover/config.ini if missing, preserving existing settings.' \
        '  4. Installs Python dependencies in pi/.venv.' \
        '  5. Configures serial access and enables the systemd service.' \
        '' \
        'The service is enabled for boot but is not started by this installer.' \
        'For /dev/serial0, the installer disables serial login and enables the UART.' \
        'This can remove serial-console access and may require a reboot.' \
        'Review configuration and hardware permissions before starting or rebooting.' \
        '' \
        'Arguments:' \
        '  install-directory  Checkout location (default: ~/oRover).' \
        '  -h, --help         Show this help and exit.' \
        '' \
        'Environment:' \
        '  OROVER_REPO_URL    Git URL for a new clone (default: https://github.com/idurz/oRover.git).'
    exit 0
fi

step="checking prerequisites"
trap 'exit_code=$?; printf "\nInstallation failed while %s (exit %s).\n" "$step" "$exit_code" >&2' ERR

printf 'Checking prerequisites for oRover installation...\n'
if [[ "$(uname -s)" != Linux ]] || ! command -v systemctl >/dev/null || ! command -v apt-get >/dev/null; then
    echo "This installer requires a Debian-based Linux system with systemd." >&2
    exit 1
fi
if [[ "$EUID" -eq 0 ]]; then
    echo "Run this installer as the user who should run oRover, not as root." >&2
    exit 1
fi

printf '\n[1/5] Installing system dependencies (sudo may request your password)...\n'
step="installing system dependencies"
sudo apt-get update
sudo apt-get install -y git python3 python3-venv
if ! python3 -c 'import RPi.GPIO' >/dev/null 2>&1; then
    printf 'RPi.GPIO is missing; installing python3-rpi.gpio.\n'
    sudo apt-get install -y python3-rpi.gpio
else
    printf 'RPi.GPIO is already available.\n'
fi

printf '\n[2/5] Preparing repository at %s...\n' "$INSTALL_DIR"
step="preparing the repository"
if [[ -e "$INSTALL_DIR" ]]; then
    if [[ ! -e "$INSTALL_DIR/.git" ]]; then
        echo "Install directory exists but is not a Git checkout: $INSTALL_DIR" >&2
        exit 1
    fi
    printf 'Existing checkout found; pulling fast-forward updates.\n'
    git -C "$INSTALL_DIR" pull --ff-only
else
    printf 'Cloning repository into %s.\n' "$INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

INSTALL_DIR="$(cd "$INSTALL_DIR" && pwd -P)"
PI_DIR="$INSTALL_DIR/pi"
CONFIG_DIR="/etc/orover"
CONFIG_FILE="$CONFIG_DIR/config.ini"
printf '\n[3/5] Preparing configuration...\n'
step="preparing configuration"
if sudo test -f "$CONFIG_FILE"; then
    printf 'Keeping existing configuration: %s\n' "$CONFIG_FILE"
else
    if ! sudo test -d "$CONFIG_DIR"; then
        sudo install -d -m 0755 "$CONFIG_DIR"
    fi
    if [[ -f "$PI_DIR/config.ini" ]]; then
        CONFIG_SOURCE="$PI_DIR/config.ini"
    else
        CONFIG_SOURCE="$PI_DIR/config/config.example.ini"
    fi
    printf 'Creating %s from %s.\n' "$CONFIG_FILE" "$CONFIG_SOURCE"
    sudo install -m 0640 -o root -g "$(id -gn)" "$CONFIG_SOURCE" "$CONFIG_FILE"
fi

printf '\n[4/5] Creating an isolated Python environment and installing dependencies...\n'
step="installing Python dependencies"
python3 -m venv "$PI_DIR/.venv"
VENV_SITE="$("$PI_DIR/.venv/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
for module in RPi lgpio _lgpio; do
    MODULE_PATH="$(python3 -c 'import importlib.util, sys; spec = importlib.util.find_spec(sys.argv[1]); print(next(iter(spec.submodule_search_locations)) if spec and spec.submodule_search_locations else spec.origin if spec else "")' "$module")"
    if [[ -n "$MODULE_PATH" ]]; then
        ln -sfn "$MODULE_PATH" "$VENV_SITE/$(basename "$MODULE_PATH")"
    fi
done
"$PI_DIR/.venv/bin/python" -m pip install pyzmq setproctitle flask flask-socketio pyserial
printf 'Checking Python imports, including RPi.GPIO...\n'
"$PI_DIR/.venv/bin/python" -c 'import flask, flask_socketio, serial, setproctitle, zmq, RPi.GPIO'

escape_systemd() {
    local value="$1"
    value="${value//\\/\\\\}"
    value="${value//\"/\\\"}"
    value="${value//%/%%}"
    printf '%s' "$value"
}

if [[ "$PI_DIR" == *$'\n'* || "$PI_DIR" == *$'\r'* ]]; then
    echo "Install paths containing newlines are not supported." >&2
    exit 1
fi
SERVICE_DIR="$(escape_systemd "$PI_DIR")"
WORKING_DIR="${PI_DIR//%/%%}"
SERVICE_PATH="$(escape_systemd "$PI_DIR/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")"
SERVICE_USER="$(id -un)"

printf '\n[5/5] Creating and enabling the systemd service for user %s...\n' "$SERVICE_USER"
step="configuring the systemd service"
SERIAL_PORT="$(sudo python3 -c 'import configparser, sys; config = configparser.RawConfigParser(); config.read(sys.argv[1]); print(config.get("serial", "port", fallback="/dev/ttyUSB0"))' "$CONFIG_FILE")"
if [[ "$SERIAL_PORT" == "/dev/serial0" ]]; then
    if command -v raspi-config >/dev/null; then
        printf 'Disabling serial login and enabling the Raspberry Pi UART for %s...\n' "$SERIAL_PORT"
        sudo raspi-config nonint do_serial 2
        printf 'Reboot may be required for serial settings to take effect; serial login will no longer be available.\n'
    else
        printf 'Warning: raspi-config not found; configure the serial console and UART manually.\n' >&2
    fi
else
    printf 'Serial port is %s; leaving Raspberry Pi UART settings unchanged.\n' "$SERIAL_PORT"
fi
if getent group dialout >/dev/null; then
    if [[ " $(id -nG "$SERVICE_USER") " == *" dialout "* ]]; then
        printf 'User %s is already in the dialout group.\n' "$SERVICE_USER"
    else
        printf 'Adding user %s to the dialout group for serial access.\n' "$SERVICE_USER"
        sudo usermod -a -G dialout "$SERVICE_USER"
        printf 'Restart an existing oRover service to apply the new group membership.\n'
    fi
else
    printf 'Warning: dialout group not found; configure serial device permissions manually.\n' >&2
fi
printf '%s\n' \
    '[Unit]' \
    'Description=oRover robot controller' \
    'After=network.target' \
    '' \
    '[Service]' \
    'Type=simple' \
    "User=$SERVICE_USER" \
    "WorkingDirectory=$WORKING_DIR" \
    "Environment=\"PATH=$SERVICE_PATH\"" \
    "ExecStart=\"$SERVICE_DIR/.venv/bin/python\" \"$SERVICE_DIR/launcher.py\" --config=$CONFIG_FILE" \
    'Restart=on-failure' \
    'RestartSec=2' \
    'KillMode=mixed' \
    'TimeoutStopSec=15' \
    '' \
    '[Install]' \
    'WantedBy=multi-user.target' | sudo tee /etc/systemd/system/orover.service >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable orover.service

printf '\noRover installed in %s\n' "$INSTALL_DIR"
printf 'Service enabled for boot; it has not been started by the installer.\n'
printf 'Review %s and serial/GPIO permissions before starting or rebooting.\n' "$CONFIG_FILE"
printf 'Start and check the service with:\n'
printf '  sudo systemctl start orover.service\n'
printf '  sudo systemctl status orover.service\n'