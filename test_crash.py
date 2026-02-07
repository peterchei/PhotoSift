import os, sys
import logging

print("Test import starting...")

try:
    print("Importing torch...")
    import torch
    print(f"Torch version: {torch.__version__}")
    
    print("Importing cv2...")
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
    
    print("Importing PIL...")
    from PIL import Image, ImageTk
    
    print("Importing transformers...")
    from transformers import CLIPModel, CLIPProcessor
    
    print("Importing tkinter...")
    import tkinter as tk
    
    print("All imports successful!")
    
    root = tk.Tk()
    print("Tk root created")
    root.withdraw()
    
    print("Creating CLIP model...")
    model_id = "openai/clip-vit-base-patch32"
    # Use local path if exists
    local_path = os.path.join('/home/peterchei/projects/PhotoSift/models', 'clip-vit-base-patch32')
    if os.path.exists(local_path):
        model_id = local_path
    
    model = CLIPModel.from_pretrained(model_id)
    processor = CLIPProcessor.from_pretrained(model_id)
    print("CLIP model loaded")
    
    print("Success!")
    root.destroy()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
