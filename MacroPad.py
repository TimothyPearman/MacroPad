import time
import serial
import serial.tools.list_ports
import tkinter as tk
import threading 

data = "no data found :C"   # global variable to store data from Arduino for GUI access

class Arduino:
    def __init__(self):
        self.arduino = None                # default to no Arduino serial connection
        self.connected = False             # flag to track connection status
        self.handshakeResponse = "timmy"   # expected response from Arduino to confirm correct connection

    def loop(self):
        while True:
            if (self.connected):                                # if connected to Arduino, start reading data
                try:
                    if self.arduino.is_open:                    # check if the port is still open before trying to read data
                        self.get_data()                         # get arduino data
                        
                except Exception as e:                          # handle any errors that occur during data retrieval
                    print(f"Error getting data: {e}", end="")   # debug
                    if self.arduino:
                        self.arduino.close()                    # close the port safely if it's open
                    self.connected = False                      # update connection status
                    self.arduino = None                         # reset Arduino connection to trigger reconnection
                    #time.sleep(1)                              # wait before trying to reconnect
            else:
                self.get_connection()                           # attempt to connect only when disconnected

    def get_connection(self):
        ports = serial.tools.list_ports.comports()      # get a list of all available serial ports

        print("\033[H \033[J", end="")                  # move to top and clear console to remove previous connection attempts
        print("\rWaiting for Arduino...", end="")       # debug

        if not ports:                                   # if no ports are found, wait for Arduino to be plugged in
                return

        time.sleep(1)                                   # delay to allow for arduino to initialize after being plugged in
        for port in ports:                              # if a port if found, attempt to connect
            print(f"\nFound port: {port}", end="")      # debug
            if self.verify_handshake(port):             # ensure its the correct Arduino
                return

    def verify_handshake(self, port):
        try:
            self.arduino = serial.Serial(port=port.device, baudrate=115200, timeout=0.1)    # open communication with Arduino
            print(f"    Connected to {port}")                                               # debug
            self.connected = True                                                           # dev mode: mark connected on successful open
            return True

            # ! do not handshake during development, i cant be bothered to change the firmware, change later
            """ 
            response = self.arduino.readline().decode('utf-8').strip()                      # read a line of serial data and remove extra whitespace

            if response == self.handshakeResponse:                                          # if handshake response is correct, confirm connection
                print("Handshake successful :D")                                            # debug
                self.connected = True                                                       # update connection status
            else:
                print("Handshake failed :C")                                                # debug
            """

        except serial.SerialException as e:
            print(f"    Error connecting to {port.device}: {e}", end="\r")                  # debug 
            self.connected = False
            self.arduino = None
            time.sleep(1)
            return False
        except Exception as e:
            print(f"    Error during handshake with {port.device}: {e}", end="\r")          # debug 
            self.connected = False
            self.arduino = None
            time.sleep(1)
            return False

    def get_data(self):
            if self.arduino is None:
                return
            
            try:
                if self.arduino.in_waiting > 0:                                 # check if data is available from Arduino
                    global data
                    data = self.arduino.readline().decode('utf-8').strip()      # read a line of serial data and remove extra whitespace
                    
                    if data:                                                    # if the data is not empty
                        print(f"data:  {data}")                                 # debug
                        print("\033[A", end="")                                 # debug

                        # ! temporary solution
                        with open("temp.txt","w") as temp:                      # print data to temp.txt for the GUI to read and display
                            temp.write(data)

            except Exception as e:                                              # handle error if reading fails
                print("\033[1A", end="")
                print(f"Error reading from serial port: {e}", end="")           # debug   
                self.arduino.close()                                            # close the port safely
                self.arduino = None                                             # reset Arduino connection to trigger reconnection
                time.sleep(1)

class GUI:
    def __init__(self):
        self.root = tk.Tk()             # create a new Tkinter window
        self.title = "no data found"    # initialize data and title variables

        self.display_GUI()              # display the GUI
        #self.read_data()               # read data from temp
        self.show_data()                # update the GUI with the current data
        self.root.mainloop()            # start the Tkinter event loop

    def show_data(self):
        global data
        self.title.config(text=f"Count: {data}")    # update the label text with the current data value

        self.root.after(10, self.show_data)         # schedule this function to run again after 10 milliseconds to continuously update the GUI with new data

    def display_GUI(self):
        self.root.title("MacroPad")
        x = 1920 // 2
        y = 1080 // 2                                                       # get relative screen resolution
        self.root.geometry(f"{x}x{y}")

        #my_var = tk.IntVar()
        #my_var.set(0)                                                      # set the window size

        self.title = tk.Label(self.root, text="", font=("Arial", 16))       # create a label to display status
        self.title.pack(pady=20)     
    
        #label = tk.Label(root, textvariable=my_var)
        #label.pack()                                                       # add padding around the label

        button = tk.Button(self.root, text="Exit", command=self.root.quit)  # create an exit button
        button.pack(pady=10)                                                # add padding around the button

def start(cls):
    instance = cls()    # create an instance of the class
    instance.loop()     # call the loop method to start the class's main functionality

thread1 = threading.Thread(target=start, args=(Arduino,))   # thread to run the Arduino class in parallel
thread2 = threading.Thread(target=start, args=(GUI,))       # thread to run the GUI class in parallel

if __name__ == "__main__":
    thread1.start()
    time.sleep(1)       # delay to ensure Arduino thread initializes before GUI starts
    thread2.start()
