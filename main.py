import tkinter as tk
import multiprocessing
from PIL import ImageGrab, ImageTk
from time import sleep
import numpy as np


def flatten_list(nested_list):
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(int(item))
    return flattened


def getAreaWindow(shared_dictionary):
    window = tk.Tk()
    window.attributes("-alpha", 0.4)
    window.wm_attributes("-topmost", 1)
    window.configure(bg="")
    window.config(bg="#FFFFFF")
    window.geometry("300x300")

    def printWindowDimensions():
        width = window.winfo_width()
        height = window.winfo_height()
        geometry = window.winfo_geometry()
        result = geometry.split("+")
        result[0] = result[0].split("x")
        result = flatten_list(result)
        result[2] -= result[2] - window.winfo_rootx()
        result[3] -= result[3] - window.winfo_rooty()
        if shared_dictionary["coordinates"] != result:
            shared_dictionary["coordinates"] = result

        window.after(100, printWindowDimensions)

    printWindowDimensions()

    window.mainloop()


def setScreenPart(shared_dictionary, screen_changed_event):
    window = tk.Tk()

    label = tk.Label(window)
    window.wm_attributes("-topmost", 1)
    label.pack()
    def checkImage():
        width, height, x, y = shared_dictionary["coordinates"]
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        pixels = np.array(screenshot)
        screenshot_tk = ImageTk.PhotoImage(screenshot)

        # Update the image of the label
        label.config(image=screenshot_tk)
        label.image = screenshot_tk
        if not np.array_equal(pixels, shared_dictionary["image"]):
            shared_dictionary["image"] = pixels
            screen_changed_event.set()
        window.after(100, checkImage)
    
    checkImage()
    window.mainloop()

        


def createAndShowControlWindow(shared_dictionary, start_detecting_event):

    def button1_click():
        print("button 1 not implemented")
    
    def button2_click():
        print("button 2 not implemented")

    window = tk.Tk()
    window.wm_attributes("-topmost", 1)
    # Create Button 1
    button1 = tk.Button(window, text="Start", command=button1_click, width=15, height=4)
    button1.pack(side=tk.LEFT)

    # Create Button 2
    button2 = tk.Button(window, text="Continous", command=button2_click, width=15, height=4)
    button2.pack(side=tk.LEFT)
    
    window.mainloop()

def main():
    manager = multiprocessing.Manager()
    shared_dictionary = manager.dict()
    shared_dictionary["coordinates"] = [0, 0, 0, 0]
    shared_dictionary["image"] = np.array(ImageGrab.grab())
    screen_changed_event = multiprocessing.Event()
    start_detecting_event = multiprocessing.Event()

    # start processes
    get_dimmensions_window = multiprocessing.Process(
        target=getAreaWindow, args=(shared_dictionary,)
    )
    get_dimmensions_window.start()

    get_dimmensions_window = multiprocessing.Process(
        target=setScreenPart, args=(shared_dictionary, screen_changed_event)
    )
    get_dimmensions_window.start()

    create_and_show_control_window = multiprocessing.Process(
        target=createAndShowControlWindow, args=(shared_dictionary, start_detecting_event)
    )
    create_and_show_control_window.start()

    # main process
    while True:
        # Get data from the queue
        screen_changed_event.wait()
        screen_changed_event.clear()
        print("It Has Changed!!!")
        print("!!")
        coordinates = shared_dictionary["coordinates"]
        if coordinates == "exit":
            exit()


if __name__ == "__main__":
    main()