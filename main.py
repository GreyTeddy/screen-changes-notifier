import tkinter as tk
import multiprocessing
import threading
from PIL import ImageGrab, ImageTk
from time import sleep
import numpy as np
import platform
os_name = platform.system()
if os_name == "Windows":
    import winsound
else:
    from playsound import playsound


def flatten_list(nested_list):
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(int(item))
    return flattened


def getAreaWindow(shared_dictionary,exit_program_event):
    window = tk.Tk()
    window.title("Select the Area")
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
    exit_program_event.set()
    exit()


def setScreenPart(shared_dictionary, screen_changed_event,raise_start_button_event,exit_program_event):
    window = tk.Tk()
    window.title("Select the Area")
    label = tk.Label(window)
    window.wm_attributes("-topmost", 1)
    label.pack()
    def checkImage():
        screenshot = getScreenPart(shared_dictionary)
        pixels = np.array(screenshot)
        screenshot_tk = ImageTk.PhotoImage(screenshot)

        # Update the image of the label
        label.config(image=screenshot_tk)
        label.image = screenshot_tk
        if not np.array_equal(pixels, shared_dictionary["image"]):
            shared_dictionary["image"] = pixels
            if shared_dictionary["check"]:
                screen_changed_event.set()
                shared_dictionary["check"] = shared_dictionary["check_continously"]
                if not shared_dictionary["check"]:
                    raise_start_button_event.set()
        window.after(10, checkImage)
    
    checkImage()
    window.mainloop()
    exit_program_event.set()
    exit()

def getScreenPart(shared_dictionary):
    width, height, x, y = shared_dictionary["coordinates"]
    return ImageGrab.grab(bbox=(x, y, x + width, y + height))
  

def createAndShowControlWindow(shared_dictionary, start_detecting_event,raise_start_button_event,exit_program_event):

    buttons_are_raised = [True,True]
    def startButtonClick():
        print("startButtonClick")
        if buttons_are_raised[0]:
            start_button_click.config(text="Checking",relief=tk.SUNKEN)
            shared_dictionary["check"] = True
            buttons_are_raised[0] = False
        else:
            start_button_click.config(text="Start",relief=tk.RAISED)
            shared_dictionary["check"] = False
            buttons_are_raised[0] = True
    
    def continousButtonClick():
        print("continousButtonClick")
        if buttons_are_raised[1]:
            continous_button_click.config(text="Checking\nContinously",relief=tk.SUNKEN)
            shared_dictionary["check_continously"] = True
            buttons_are_raised[1] = False
        else:
            continous_button_click.config(text="Check\nContinously",relief=tk.RAISED)
            shared_dictionary["check_continously"] = False
            buttons_are_raised[1] = True

    def checkForStoppingChecking():
        while True:
            raise_start_button_event.wait()
            raise_start_button_event.clear()
            start_button_click.config(text="Start",relief=tk.RAISED)
            shared_dictionary["check"] = False
            buttons_are_raised[0] = True

    window = tk.Tk()
    window.wm_attributes("-topmost", 1)
    window.title("Controls")

    start_button_click = tk.Button(window, text="Start", command=startButtonClick, width=15, height=4)
    start_button_click.pack(side=tk.LEFT, expand=True)

    continous_button_click = tk.Button(window, text="Checking\nContinously", command=continousButtonClick, width=15, height=4)
    continous_button_click.pack(side=tk.RIGHT,expand=True)
    
    start_button_raise_check= threading.Thread(target=checkForStoppingChecking)
    start_button_raise_check.daemon = True
    start_button_raise_check.start()
    window.mainloop()
    exit_program_event.set()
    exit()



def handleFoundChange(screen_changed_event,exit_program_event):
    wav_file = "camera_click.wav"
    while True:
        screen_changed_event.wait()
        screen_changed_event.clear()
        print("It Has Changed!!!")
        print("!!")
        if os_name == "Windows":
            winsound.PlaySound(wav_file, winsound.SND_FILENAME)
        else:
            playsound(wav_file)

    exit_program_event.set()


def main():
    manager = multiprocessing.Manager()
    shared_dictionary = manager.dict()
    shared_dictionary["coordinates"] = [0, 0, 0, 0]
    shared_dictionary["check_continously"] = False
    shared_dictionary["check"] = False
    shared_dictionary["image"] = np.array(ImageGrab.grab())
    screen_changed_event = multiprocessing.Event()
    start_detecting_event = multiprocessing.Event()
    raise_start_button_event = multiprocessing.Event()
    exit_program_event = multiprocessing.Event()
    # start processes

    create_and_show_control_window = multiprocessing.Process(
        target=createAndShowControlWindow, args=(shared_dictionary, start_detecting_event,raise_start_button_event,exit_program_event)
    )
    create_and_show_control_window.start()

    get_dimmensions_window = multiprocessing.Process(
        target=getAreaWindow, args=(shared_dictionary,exit_program_event)
    )
    get_dimmensions_window.start()

    get_dimmensions_window = multiprocessing.Process(
        target=setScreenPart, args=(shared_dictionary, screen_changed_event,raise_start_button_event,exit_program_event)
    )
    get_dimmensions_window.start()

    handle_found_change = multiprocessing.Process(
        target=handleFoundChange, args=(screen_changed_event,exit_program_event)
    )
    handle_found_change.start()

    # wait for exit
    exit_program_event.wait()
    get_dimmensions_window


if __name__ == "__main__":
    main()