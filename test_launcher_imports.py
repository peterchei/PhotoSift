import os, sys, time, logging, multiprocessing

print("Starting Stability Test...")

def main():
    print("Inside main...")
    
    # Setup path
    application_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(application_path, "src"))

    # 1. Imports
    try:
        print("Importing torch...")
        import torch
        print("Importing cv2...")
        import cv2
        print("Importing numpy...")
        import numpy as np
        print("Importing PIL...")
        from PIL import Image, ImageTk
        print("Importing transformers...")
        from transformers import CLIPModel, CLIPProcessor
        
        print("Importing ImageClassification...")
        import ImageClassification
        print("Importing DuplicateImageIdentifier...")
        import DuplicateImageIdentifier
        print("Importing DarkImageDetection...")
        import DarkImageDetection
        print("Importing BlurryImageDetection...")
        import BlurryImageDetection
        print("Importing CommonUI...")
        import CommonUI
        
        print("Importing ImageClassifierGUI...")
        from ImageClassifierGUI import ImageClassifierApp
        print("Importing DuplicateImageIdentifierGUI...")
        from DuplicateImageIdentifierGUI import DuplicateImageIdentifierApp
        print("Importing BlurryImageDetectionGUI...")
        from BlurryImageDetectionGUI import BlurryImageDetectionApp
        print("Importing DarkImageDetectionGUI...")
        from DarkImageDetectionGUI import DarkImageDetectionApp
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("UI modules imported successfully.")
    import tkinter as tk
    root = tk.Tk()
    print("Tk root created.")
    root.destroy()
    print("Success!")

if __name__ == "__main__":
    main()
