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
    window.config(bg="#000000")
    window.geometry("300x300")

    def printWindowDimensions():
        width = window.winfo_width()
        height = window.winfo_height()
        geometry = window.winfo_geometry()
        result = geometry.split("+")
        result[0] = result[0].split("x")
        result = flatten_list(result)
        if shared_dictionary["coordinates"] != result:
            shared_dictionary["coordinates"] = result

        window.after(100, printWindowDimensions)

    printWindowDimensions()

    window.mainloop()


def setScreenPart(shared_dictionary, screen_changed_event):
    while True:
        width, height, x, y = shared_dictionary["coordinates"]
        # Capture the screen part within the specified dimensions
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        pixels = np.array(screenshot)
        if not np.array_equal(pixels, shared_dictionary["image"]):
            shared_dictionary["image"] = pixels
            screen_changed_event.set()


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    shared_dictionary = manager.dict()
    shared_dictionary["coordinates"] = [0, 0, 0, 0]
    shared_dictionary["image"] = np.array(ImageGrab.grab())
    screen_changed_event = multiprocessing.Event()

    # start processes
    get_dimmensions_window = multiprocessing.Process(
        target=getAreaWindow, args=(shared_dictionary,)
    )
    get_dimmensions_window.start()

    get_dimmensions_window = multiprocessing.Process(
        target=setScreenPart, args=(shared_dictionary, screen_changed_event)
    )
    get_dimmensions_window.start()

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
