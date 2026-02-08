import time
import threading
ser_lock = threading.Lock()

# ---------------- CONFIG ----------------
LINEAR_SPEED = 0.3     # m/s (tune this)
ANGULAR_SPEED = 45.0   # deg/s (tune this)

CMD_PERIOD = 0.1       # seconds (10 Hz, keeps watchdog alive)
# ----------------------------------------

def send_cmd(ser, left, right):
    cmd = f'{{"T":1,"L":{left:.2f},"R":{right:.2f}}}\n'
    with ser_lock:
        ser.write(cmd.encode())

def stop(ser):
    with ser_lock:
        send_cmd(ser, 0.0, 0.0)

def drive_straight(ser, distance):
    direction = 1.0 if distance >= 0 else -1.0
    duration = abs(distance) / LINEAR_SPEED

    left = 0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        with ser_lock:
            send_cmd(ser, left, right)
            time.sleep(CMD_PERIOD)

    stop(ser)

def rotate(ser, angle_deg):
    direction = 1.0 if angle_deg >= 0 else -1.0
    duration = abs(angle_deg) / ANGULAR_SPEED

    # In-place rotation
    left = -0.3 * direction
    right = 0.3 * direction

    start = time.time()
    while time.time() - start < duration:
        with ser_lock:
            send_cmd(ser, left, right)
            time.sleep(CMD_PERIOD)

    stop(ser)
