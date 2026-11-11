#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
REAL_PYTHON="$(command -v python3)"
TEST_DIR="$(mktemp -d)"
TEST_DIR="$(cd "$TEST_DIR" && pwd -P)"
trap 'rm -rf "$TEST_DIR"' EXIT
export TEST_DIR
mkdir -p "$TEST_DIR/bin"

printf '%s\n' '#!/usr/bin/env bash' '
set -euo pipefail
name="${0##*/}"
printf "%s %s\n" "$name" "$*" >> "$TEST_DIR/commands"
case "$name" in
    uname) printf "Linux\n" ;;
    sudo)
        if [[ "$1" == test ]]; then
            builtin test "$2" "$TEST_DIR$3"
        elif [[ "$1" == install && "$2" == -d ]]; then
            mkdir -p "$TEST_DIR/etc/orover"
        elif [[ "$1" == install ]]; then
            cp "${@: -2:1}" "$TEST_DIR/etc/orover/config.ini"
        else
            "$@"
        fi
        ;;
    apt-get|systemctl) ;;
    raspi-config)
        if [[ "${TEST_RASPI_FAIL:-0}" == 1 ]]; then exit 1; fi
        ;;
    usermod)
        if [[ "${TEST_USERMOD_FAIL:-0}" == 1 ]]; then exit 1; fi
        ;;
    getent)
        if [[ "${TEST_NO_DIALOUT:-0}" == 1 ]]; then exit 1; fi
        printf "dialout:x:20:\n"
        ;;
    id)
        case "$1" in
            -un) printf "testuser\n" ;;
            -gn) printf "testgroup\n" ;;
            -nG) printf "%s\n" "${TEST_USER_GROUPS:-testgroup}" ;;
        esac
        ;;
    tee) /usr/bin/tee "$TEST_DIR/service" ;;
    git)
        if [[ "$1" == clone ]]; then
            mkdir -p "$3/.git" "$3/pi/config"
            printf "example config\n" > "$3/pi/config/config.example.ini"
            touch "$3/pi/launcher.py"
        elif [[ "${TEST_PULL_FAIL:-0}" == 1 ]]; then
            exit 1
        fi
        ;;
    python3)
        if [[ "${1:-}" == -c && "${2:-}" == "import RPi.GPIO" && "${TEST_MISSING_GPIO:-0}" == 1 ]]; then
            exit 1
        elif [[ "${1:-}" == -m && "${2:-}" == venv ]]; then
            mkdir -p "$3/bin" "$3/site-packages"
            ln -sf "$TEST_DIR/bin/python" "$3/bin/python"
        elif [[ "${1:-}" == -c && "${2:-}" == *find_spec* ]]; then
            case "${3:-}" in
                RPi) printf "%s\n" "$TEST_DIR/system/RPi" ;;
                lgpio) printf "%s\n" "$TEST_DIR/system/lgpio.py" ;;
                _lgpio) printf "%s\n" "$TEST_DIR/system/_lgpio.so" ;;
            esac
        elif [[ "${1:-}" == -c && "${2:-}" == *RawConfigParser* ]]; then
            printf "%s\n" "${TEST_SERIAL_PORT:-/dev/serial0}"
        fi
        ;;
    python)
        if [[ "${1:-}" == -c && "${2:-}" == *sysconfig* ]]; then
            printf "%s\n" "${0%/bin/python}/site-packages"
        fi
        ;;
esac' > "$TEST_DIR/bin/mock"
chmod +x "$TEST_DIR/bin/mock"
for command in uname sudo apt-get systemctl tee git python3 python getent id usermod raspi-config; do
    ln -s mock "$TEST_DIR/bin/$command"
done
export PATH="$TEST_DIR/bin:$PATH"

bash "$ROOT/install.sh" --help > "$TEST_DIR/help"
grep -Fq 'OROVER_REPO_URL' "$TEST_DIR/help"
grep -Fq 'not started by this installer' "$TEST_DIR/help"
grep -Fq 'disables serial login and enables the UART' "$TEST_DIR/help"

PYTHONDONTWRITEBYTECODE=1 "$REAL_PYTHON" -c '
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1] + "/pi")
import oroverlib
for arguments, expected in (([], "/etc/orover/config.ini"), (["--config", "/tmp/custom.ini"], "/tmp/custom.ini")):
    with patch.object(sys, "argv", ["orover"] + arguments), patch("os.path.isfile", return_value=True), patch("configparser.ConfigParser.read"):
        assert oroverlib.readConfig(True)[1] == expected
' "$ROOT"
for wrapper in "$ROOT/pi/start" "$ROOT/pi/stop"; do
    grep -Fq 'CONFIG_FILE="${1:-/etc/orover/config.ini}"' "$wrapper"
done

INSTALL_DIR="$TEST_DIR/rover with space%"
TEST_MISSING_GPIO=1 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/install-output"
grep -Fq '[1/5] Installing system dependencies' "$TEST_DIR/install-output"
grep -Fq '[5/5] Creating and enabling the systemd service' "$TEST_DIR/install-output"
grep -Fq 'Service enabled for boot; it has not been started' "$TEST_DIR/install-output"
test "$(<"$TEST_DIR/etc/orover/config.ini")" = 'example config'
grep -Fq 'git clone https://github.com/idurz/oRover.git' "$TEST_DIR/commands"
grep -Fq 'apt-get install -y python3-rpi.gpio' "$TEST_DIR/commands"
grep -Fq 'usermod -a -G dialout testuser' "$TEST_DIR/commands"
grep -Fq 'raspi-config nonint do_serial 2' "$TEST_DIR/commands"
grep -Fq 'Reboot may be required' "$TEST_DIR/install-output"
grep -Fq 'Restart an existing oRover service' "$TEST_DIR/install-output"
test -L "$INSTALL_DIR/pi/.venv/site-packages/RPi"
test -L "$INSTALL_DIR/pi/.venv/site-packages/lgpio.py"
test -L "$INSTALL_DIR/pi/.venv/site-packages/_lgpio.so"
if grep -Fq -- '--system-site-packages' "$TEST_DIR/commands"; then
    echo 'Installer must isolate system Python packages' >&2
    exit 1
fi
grep -Fxq "WorkingDirectory=$TEST_DIR/rover with space%%/pi" "$TEST_DIR/service"
grep -Fq -- '--config=/etc/orover/config.ini' "$TEST_DIR/service"
grep -Fq 'systemctl enable orover.service' "$TEST_DIR/commands"
if grep -Fq 'systemctl start' "$TEST_DIR/commands"; then
    echo 'Installer must not start the service immediately' >&2
    exit 1
fi

printf 'custom config\n' > "$INSTALL_DIR/pi/config.ini"
rm "$TEST_DIR/etc/orover/config.ini"
bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/migration-output"
test "$(<"$TEST_DIR/etc/orover/config.ini")" = 'custom config'
printf 'system config\n' > "$TEST_DIR/etc/orover/config.ini"
USERMOD_COUNT="$(grep -Fc 'usermod -a -G dialout testuser' "$TEST_DIR/commands")"
TEST_USER_GROUPS='testgroup dialout' bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/update-output"
grep -Fq 'pulling fast-forward updates' "$TEST_DIR/update-output"
grep -Fq 'Keeping existing configuration' "$TEST_DIR/update-output"
grep -Fq 'already in the dialout group' "$TEST_DIR/update-output"
test "$(grep -Fc 'usermod -a -G dialout testuser' "$TEST_DIR/commands")" = "$USERMOD_COUNT"
test "$(<"$TEST_DIR/etc/orover/config.ini")" = 'system config'
grep -Fq 'pull --ff-only' "$TEST_DIR/commands"

TEST_NO_DIALOUT=1 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/no-dialout-output" 2>&1
grep -Fq 'dialout group not found' "$TEST_DIR/no-dialout-output"
test "$(grep -Fc 'usermod -a -G dialout testuser' "$TEST_DIR/commands")" = "$USERMOD_COUNT"

SERIAL_SETUP_COUNT="$(grep -Fc 'raspi-config nonint do_serial 2' "$TEST_DIR/commands")"
TEST_SERIAL_PORT=/dev/ttyUSB0 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/usb-output"
grep -Fq 'leaving Raspberry Pi UART settings unchanged' "$TEST_DIR/usb-output"
test "$(grep -Fc 'raspi-config nonint do_serial 2' "$TEST_DIR/commands")" = "$SERIAL_SETUP_COUNT"

rm "$TEST_DIR/bin/raspi-config"
bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/no-raspi-output" 2>&1
grep -Fq 'raspi-config not found' "$TEST_DIR/no-raspi-output"
ln -s mock "$TEST_DIR/bin/raspi-config"

if TEST_RASPI_FAIL=1 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/raspi-failure-output" 2>&1; then
    echo 'Installer must fail if serial configuration fails' >&2
    exit 1
fi
grep -Fq 'Installation failed while configuring the systemd service' "$TEST_DIR/raspi-failure-output"

if TEST_USERMOD_FAIL=1 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/group-failure-output" 2>&1; then
    echo 'Installer must fail if serial group membership cannot be changed' >&2
    exit 1
fi
grep -Fq 'Installation failed while configuring the systemd service' "$TEST_DIR/group-failure-output"

if TEST_PULL_FAIL=1 bash "$ROOT/install.sh" "$INSTALL_DIR" > "$TEST_DIR/failure-output" 2>&1; then
    echo 'Installer must fail if the checkout cannot be updated' >&2
    exit 1
fi
grep -Fq 'Installation failed while preparing the repository' "$TEST_DIR/failure-output"
test "$(<"$TEST_DIR/etc/orover/config.ini")" = 'system config'
printf 'Installer tests passed.\n'