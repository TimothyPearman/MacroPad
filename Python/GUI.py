import time
import serial
import serial.tools.list_ports
import tkinter as tk

class GUI:
    def __init__(self):
        self.root = tk.Tk()                                                                     # create a new Tkinter window
        self.data = ""
        self.title = None

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

        self.title = tk.Label(self.root, text="MacroPad is running...", font=("Arial", 16))     # create a label to display status
        self.title.pack(pady=20)    
    
        #label = tk.Label(root, textvariable=my_var)
        #label.pack()                                                                           # add padding around the label

        button = tk.Button(self.root, text="Exit", command=self.root.quit)                      # create an exit button
        button.pack(pady=10)                                                                    # add padding around the button

if __name__ == "__main__":
    gui = GUI()                                                                                 # create GUI instance
    gui.display_GUI()                                                                           # display the GUI
    gui.read_data()                                                                             # read data from temp
    gui.root.mainloop()                                                                         # start the Tkinter event loop
