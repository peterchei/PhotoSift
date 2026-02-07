import sys, os

def test_import(name):
    print(f"Testing import of {name}...", end=" ", flush=True)
    try:
        __import__(name)
        print("SUCCESS")
    except Exception as e:
        print(f"FAILED: {e}")

test_import("torch")
test_import("cv2")
test_import("numpy")
test_import("PIL.Image")
test_import("PIL.ImageTk")
test_import("transformers")
test_import("tkinter")

print("\nAll individual imports checked.")

print("Checking combined import of torch + tkinter...")
import torch
import tkinter as tk
root = tk.Tk()
print("Tk root created after torch.")
root.destroy()
print("Done.")
