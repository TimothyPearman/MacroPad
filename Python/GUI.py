import time
import serial
import serial.tools.list_ports
import tkinter as tk

root = tk.Tk()                                                                      # create a new Tkinter window

def read_data():
    with open("temp.txt", "r") as temp:
        line = temp.readlines()
        if line:
            line = line[-1].strip()
            print("\033[H\033[2B\033[G", end="") # move to top, move down 2 lines
            print(f"Gui:   {line}")
        #else:
            #print("no data found in temp.txt")
    
    root.after(10, read_data)

def display_GUI():
    root.title("MacroPad")     
    x = 1920 // 2
    y = 1080 // 2                                                                   # get relative screen resolution
    root.geometry(f"{x}x{y}")   
    
    #my_var = tk.IntVar()
    #my_var.set(0)                                                                   # set the window size

    title = tk.Label(root, text="MacroPad is running...", font=("Arial", 16))       # create a label to display status
    title.pack(pady=20)    
    
    #label = tk.Label(root, textvariable=my_var)
    #label.pack()                                                                    # add padding around the label

    button = tk.Button(root, text="Exit", command=root.quit)                        # create an exit button
    button.pack(pady=10)                                                            # add padding around the button

if __name__ == "__main__":
    display_GUI()                                                                   # display the GUI
    read_data()                                                                     # read data from temp
    root.mainloop()                                                                 # start the Tkinter event loop