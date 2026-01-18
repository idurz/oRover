import serial
import time
import argparse
import math

# ---------------- CONFIG ----------------
UART_PORT = "/dev/serial0"
BAUDRATE = 115200

LINEAR_SPEED = 0.3     # m/s (tune this)
ANGULAR_SPEED = 45.0   # deg/s (tune this)

CMD_PERIOD = 0.1       # seconds (10 Hz, keeps watchdog alive)
# ----------------------------------------


def send_cmd(ser, left, right):
    cmd = f'{{"T":1,"L":{left:.2f},"R":{right:.2f}}}\n'
    ser.write(cmd.encode())


def stop(ser):
    send_cmd(ser, 0.0, 0.0)


def drive_straight(ser, distance):
    direction = 1.0 if distance >= 0 else -1.0
    duration = abs(distance) / LINEAR_SPEED

    left = 0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        send_cmd(ser, left, right)
        time.sleep(CMD_PERIOD)
 # CVK17012026 - See response 
 #       print(ser.read_all())

    stop(ser)


def rotate(ser, angle_deg):
    direction = 1.0 if angle_deg >= 0 else -1.0
    duration = abs(angle_deg) / ANGULAR_SPEED

    # In-place rotation
    left = -0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        send_cmd(ser, left, right)
        time.sleep(CMD_PERIOD)

    stop(ser)


def main():
    parser = argparse.ArgumentParser(description="Drive UGV01 by distance and angle")
    parser.add_argument("--distance", type=float, required=True,
                        help="Distance in meters (positive = forward)")
    parser.add_argument("--angle", type=float, required=True,
                        help="Angle in degrees (positive = left turn)")
    args = parser.parse_args()

    ser = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # allow UART to settle

    print(f"Driving {args.distance} m")
    drive_straight(ser, args.distance)

    time.sleep(0.5)

    print(f"Turning {args.angle} degrees")
    rotate(ser, args.angle)

    ser.close()
    print("Done.")


if __name__ == "__main__":
    main()
