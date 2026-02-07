"""
PhotoSift Application Launcher
Final Stability Version
"""

import os, sys, time, logging, multiprocessing

# Configure logging
log_dir = os.path.join(os.path.expanduser('~'), 'PhotoSift', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'photosift_app.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)])
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting PhotoSift...")
    
    # Setup path
    application_path = os.path.dirname(os.path.abspath(__file__))
    if application_path not in sys.path:
        sys.path.insert(0, application_path)

    # 1. Imports
    try:
        import torch
        import cv2
        import numpy as np
        from PIL import Image, ImageTk
        from transformers import CLIPModel, CLIPProcessor
        
        import ImageClassification
        import DuplicateImageIdentifier
        import DarkImageDetection
        import BlurryImageDetection
        import CommonUI
        
        from ImageClassifierGUI import ImageClassifierApp
        from DuplicateImageIdentifierGUI import DuplicateImageIdentifierApp
        from BlurryImageDetectionGUI import BlurryImageDetectionApp
        from DarkImageDetectionGUI import DarkImageDetectionApp
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return

    # 2. UI Setup
    import tkinter as tk
    root = tk.Tk()
    root.title("PhotoSift")
    root.geometry("500x500")
    root.configure(bg='#1e293b')
    
    # Optional: Set icon (safe version)
    try:
        icon_path = os.path.join(os.path.dirname(application_path), "resources", "app.ico")
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            icon_img = ImageTk.PhotoImage(img.resize((32, 32)))
            root.wm_iconphoto(True, icon_img)
            root._icon = icon_img
    except: pass

    tk.Label(root, text="PhotoSift", font=("Segoe UI", 24, "bold"), 
             bg='#1e293b', fg='#3b82f6').pack(pady=20)
    
    btn_frame = tk.Frame(root, bg='#1e293b')
    btn_frame.pack(fill=tk.X, padx=60)

    def launch_tool(cls):
        # We don't hide root here for maximum stability during test
        tool_win = tk.Toplevel(root)
        app = cls(tool_win)

    apps = [
        ("🧹 Identify Unwanted Photos", ImageClassifierApp, '#3b82f6'),
        ("🔍 Identify Duplicate Photos", DuplicateImageIdentifierApp, '#10b981'),
        ("🌫️ Detect Blurry Photos", BlurryImageDetectionApp, '#f97316'),
        ("🌑 Detect Dark Photos", DarkImageDetectionApp, '#64748b')
    ]

    for text, cls, color in apps:
        tk.Button(btn_frame, text=text, command=lambda c=cls: launch_tool(c),
                 font=("Segoe UI", 12, "bold"), bg=color, fg='white',
                 bd=0, relief=tk.FLAT, cursor="hand2", pady=10).pack(pady=8, fill=tk.X)

    logger.info("Launcher ready.")
    root.mainloop()

if __name__ == "__main__":
    if hasattr(multiprocessing, 'freeze_support'):
        multiprocessing.freeze_support()
    main()
