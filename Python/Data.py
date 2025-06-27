import time
import serial
import serial.tools.list_ports

def find_arduino():
    ports = serial.tools.list_ports.comports()                                      # list all available active serial ports
    return ports[0].device if ports else None                                       # return the device name of the first port if available

arduino = None                                                                      # default to no Arduino serial connection

while True:
    if arduino is None or not arduino.is_open:                                      # check if Arduino is connected or the port is closed
        print("\033[2J\033[H", end="")

        port = find_arduino()                                                       # try to find an available port
        if port:                                                                    # if a port is found
            try:
                arduino = serial.Serial(port=port, baudrate=115200, timeout=0.1)    # open communication with Arduino
                print(f"Connected to {port}")
            except serial.SerialException as e:                                     # handle error if port can't be opened
                print(f"\rError connecting to {port}: {e}", end="")
                time.sleep(1) 
                continue
        else:                                                                       # no port found, waiting for Arduino to be plugged in
            print("\rWaiting for Arduino...", end="")
            time.sleep(1)
            continue

    try:
        if arduino.in_waiting > 0:                                                  # check if data is available from Arduino
            data = arduino.readline().decode('utf-8').strip()                       # read a line of serial data and remove extra whitespace
            if data:                                                                # if the data is not empty
                #print(f"{data[:4]}\n{data[4:8]}\n{data[8:12]}\n", end="")           # print state for each key
                #print(f"\033[3A\033[G", end="")                                     # move cursor to start to overwrite old data

                print("\033[H\033[B\033[G", end="") # move to top, move down 2 lines
                print(f"data:  {data}")
                #print("\033[A\033[G", end="")

                with open("temp.txt","w") as temp:
                    temp.write(data)

    except Exception as e:                                                          # handle error if reading fails
        print(f"Error reading from serial port: {e}", end="")
        arduino.close()                                                             # close the port safely
        arduino = None                                                              # reset Arduino connection to trigger reconnection
        time.sleep(1)