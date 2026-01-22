import serial
import time
import argparse
import math
import csv

# ---------------- CONFIG ----------------
UART_PORT = "/dev/serial0"
BAUDRATE = 115200

LINEAR_SPEED = 0.3     # m/s (tune this)
ANGULAR_SPEED = 45.0   # deg/s (tune this)

CMD_PERIOD = 0.1       # seconds (10 Hz, keeps watchdog alive)
# ----------------------------------------
commands = []

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
    #Input straight distance and angle in pairs and save it to disk and execute the input, or read file and execute?
    rwfile = input("Write file and process or read file 'commands.csv' (w/r): ").lower()

    if rwfile != "r":
        #clean file to do new recording
        with open("commands.csv", "w") as f:
            pass
        #input 
        while True:
            distance = float(input("Enter distance: "))
            angle = float(input("Enter degrees: "))

            commands.append((distance, angle))

            cont = input("Add another command? (y/n): ").lower()
            if cont != "y":
                break
        #save to file    
        with open("commands.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["distance", "angle"])  # header
            for cmd in commands:
                writer.writerow(cmd)   
            # Clear input stored in memory (list) 
            commands.clear()                        

    #open file and fill commands
    with open("commands.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            commands.append((float(row["distance"]), float(row["angle"])))

    ser = serial.Serial(UART_PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # allow UART to settle

    #execute commands
    for distance, angle in commands:
        print(f"Driving {distance} m")
        drive_straight(ser, distance)

        time.sleep(0.5)

        print(f"Turning {angle} degrees")
        rotate(ser, angle)

    ser.close()
    print("Done.")


if __name__ == "__main__":
    main()
