import time
import serial
import serial.tools.list_ports
import tkinter as tk
import threading 



class Arduino:
    def __init__(self):
        self.arduino = None                                                                         # default to no Arduino serial connection

        self.get_data()                                                                             # get arduino data


    def find_arduino(self):
        ports = serial.tools.list_ports.comports()                                                  # list all available active serial ports
        return ports[0].device if ports else None                                                   # return the device name of the first port if available

    def get_data(self):
        while True:
            if self.arduino is None or not self.arduino.is_open:                                    # check if Arduino is connected or the port is closed
                print("\033[2J\033[H", end="")                                                     #debug

                port = self.find_arduino()                                                          # try to find an available port
                if port:                                                                            # if a port is found
                    try:
                        self.arduino = serial.Serial(port=port, baudrate=115200, timeout=0.1)       # open communication with Arduino
                        print(f"Connected to {port}")                                              #debug
                    except serial.SerialException as e:                                             # handle error if port can't be opened
                        print(f"\rError connecting to {port}: {e}", end="")                        #debug
                        time.sleep(1) 
                        continue
                else:                                                                               # no port found, waiting for Arduino to be plugged in
                    print("\rWaiting for Arduino...", end="")                                      #debug
                    time.sleep(1)
                    continue

            try:
                if self.arduino.in_waiting > 0:                                                     # check if data is available from Arduino
                    data = self.arduino.readline().decode('utf-8').strip()                          # read a line of serial data and remove extra whitespace
                    if data:                                                                        # if the data is not empty
                        #print(f"{data[:4]}\n{data[4:8]}\n{data[8:12]}\n", end="")                  # print state for each key
                        #print(f"\033[3A\033[G", end="")                                            # move cursor to start to overwrite old data

                        print("\033[H\033[B\033[G", end="")                                        #debug
                        print(f"data:  {data}")                                                    #debug
                        print("\033[A\033[G", end="")                                              #debug

                        with open("temp.txt","w") as temp:
                            temp.write(data)

            except Exception as e:                                                                  # handle error if reading fails
                print(f"Error reading from serial port: {e}", end="")                              #debug   
                arduino.close()                                                                     # close the port safely
                arduino = None                                                                      # reset Arduino connection to trigger reconnection
                time.sleep(1)
                                                                         # create Arduinoinstance

class GUI:
    def __init__(self):
        self.root = tk.Tk()                                                                     # create a new Tkinter window
        self.data = ""
        self.title = None

        self.display_GUI()                                                                           # display the GUI
        self.read_data()                                                                             # read data from temp
        self.root.mainloop()                                                                         # start the Tkinter event loop

    def read_data(self):
        with open("temp.txt", "r") as temp:
            line = temp.readlines()
            if line:
                self.data = line[-1].strip()
                self.title.config(text=f"Count: {self.data}")

            #print("\033[H\033[2B\033[G", end="") # move to top, move down 2 lines              #debug
            #print(f"Gui:   {self.data}")                                                       #debug
        #else:
            #print("no data found in temp.txt")

        self.root.after(10, self.read_data)

    def display_GUI(self):
        self.root.title("MacroPad")
        x = 1920 // 2
        y = 1080 // 2                                                                           # get relative screen resolution
        self.root.geometry(f"{x}x{y}")

        #my_var = tk.IntVar()
        #my_var.set(0)                                                                          # set the window size

        self.title = tk.Label(self.root, text="", font=("Arial", 16))     # create a label to display status
        self.title.pack(pady=20)     
    
        #label = tk.Label(root, textvariable=my_var)
        #label.pack()                                                                           # add padding around the label

        button = tk.Button(self.root, text="Exit", command=self.root.quit)                      # create an exit button
        button.pack(pady=10)                                                                    # add padding around the button

def start(cls):
    instance = cls()
    instance.loop()

thread1 = threading.Thread(target=start, args=(Arduino,))
thread2 = threading.Thread(target=start, args=(GUI,))

if __name__ == "__main__":
    thread1.start()
    time.sleep(1)
    thread2.start()