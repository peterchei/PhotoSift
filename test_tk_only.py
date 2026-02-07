import tkinter as tk
import sys
import os

print("Simple Tk test starting...")
try:
    root = tk.Tk()
    print("Tk root created.")
    root.title("Test")
    root.update()
    print("Tk update successful.")
    root.destroy()
    print("SUCCESS!")
except Exception as e:
    print(f"Error: {e}")
