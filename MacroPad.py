import time
import serial
import serial.tools.list_ports


ports = serial.tools.list_ports.comports() # list all available active serial ports
arduino = serial.Serial(port=ports[0].device, baudrate=115200, timeout=0.1) # open communication with the first available active port

while True:
    if arduino.in_waiting > 0:  # check if data is available
        data = arduino.readline().decode('utf-8').strip() # read a line of serial data
        if data:
            print(f"\n{data[:4]}\n{data[4:8]}\n{data[8:12]}", end="") # slice data into rows
            print(f"\033[{3}A", end="") # overwrite the previous output for legibility

