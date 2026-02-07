import os, sys, time, threading, logging

print("Full Test Import starting...")

def test():
    print("Importing AI stack...")
    import torch
    import cv2
    import numpy as np
    from PIL import Image, ImageTk
    from transformers import CLIPModel, CLIPProcessor
    print("AI stack imported.")

    print("Importing local modules...")
    sys.path.insert(0, os.path.abspath('src'))
    import ImageClassification
    import DuplicateImageIdentifier
    import DarkImageDetection
    import BlurryImageDetection
    import CommonUI
    print("Local modules imported.")

    print("Creating Tk root...")
    import tkinter as tk
    root = tk.Tk()
    root.title("PhotoSift Test")
    print("Tk root created.")

    print("Preloading model...")
    DuplicateImageIdentifier.load_models()
    print("Model preloaded.")

    print("Refreshing UI...")
    root.update()
    time.sleep(1)
    
    print("Destroying root...")
    root.destroy()
    print("SUCCESS!")

if __name__ == "__main__":
    test()
