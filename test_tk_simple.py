import tkinter as tk
import sys

print(f"Python version: {sys.version}")
try:
    root = tk.Tk()
    root.title("Test")
    root.geometry("200x100")
    label = tk.Label(root, text="Hello Tkinter")
    label.pack()
    root.update()
    print("Tkinter update successful")
    root.destroy()
    print("Tkinter destroy successful")
except Exception as e:
    print(f"Tkinter error: {e}")
