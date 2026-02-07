"""
PhotoSift Application Launcher
Final Stability Version (Cross-Platform)
"""

import os
import sys
import platform

# 1. SETUP PATH
application_path = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(application_path) == 'src':
    src_dir = application_path
    root_dir = os.path.dirname(application_path)
else:
    src_dir = os.path.join(application_path, 'src')
    root_dir = application_path

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def main():
    IS_WINDOWS = platform.system() == "Windows"
    
    # 2. LOAD AI STACK
    print("Loading AI core components...")
    try:
        import numpy as np
        from PIL import Image, ImageTk
        import cv2
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except Exception as e:
        print(f"Failed to load AI stack: {e}")
        return

    # 3. LOAD APPLICATION LOGIC
    print("Loading application logic...")
    try:
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
        print(f"Failed to load modules: {e}")
        return

    # 4. INITIALIZE UI
    print("Initializing User Interface...")
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.title("PhotoSift")
    root.geometry("500x550")
    root.configure(bg='#1e293b')
    
    # Safe Icon handling (Windows only for .ico)
    if IS_WINDOWS:
        try:
            icon_path = os.path.join(root_dir, "resources", "app.ico")
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except: pass
    else:
        # Linux/macOS safe icon
        try:
            icon_path = os.path.join(root_dir, "resources", "app.ico")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                icon_img = ImageTk.PhotoImage(img.resize((32, 32)))
                root.wm_iconphoto(True, icon_img)
                root._icon = icon_img
        except: pass

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (550 // 2)
    root.geometry(f"+{x}+{y}")

    # Use safe fonts and text
    main_font = ("Segoe UI", 26, "bold") if IS_WINDOWS else ("Arial", 24, "bold")
    sub_font = ("Segoe UI", 12) if IS_WINDOWS else ("Arial", 11)
    btn_font = ("Segoe UI", 12, "bold") if IS_WINDOWS else ("Arial", 11, "bold")

    tk.Label(root, text="PhotoSift", font=main_font, 
             bg='#1e293b', fg='#3b82f6').pack(pady=(40, 10))
    
    tk.Label(root, text="AI-Powered Image Management", font=sub_font, 
             bg='#1e293b', fg='#94a3b8').pack(pady=(0, 30))
    
    btn_frame = tk.Frame(root, bg='#1e293b')
    btn_frame.pack(fill=tk.X, padx=60)

    def launch_tool(cls):
        try:
            tool_win = tk.Toplevel(root)
            # Standard geometry for Linux stability
            if not IS_WINDOWS:
                sw = root.winfo_screenwidth()
                sh = root.winfo_screenheight()
                tool_win.geometry(f"{sw}x{sh}+0+0")
            app = cls(tool_win)
        except Exception as e:
            print(f"Tool launch failed: {e}")
            messagebox.showerror("Error", str(e))

    # Remove emojis on Linux to prevent font-renderer crashes
    apps = [
        (("🧹 " if IS_WINDOWS else "") + "Identify Unwanted Photos", ImageClassifierApp, '#3b82f6'),
        (("🔍 " if IS_WINDOWS else "") + "Identify Duplicate Photos", DuplicateImageIdentifierApp, '#10b981'),
        (("🌫️ " if IS_WINDOWS else "") + "Detect Blurry Photos", BlurryImageDetectionApp, '#f97316'),
        (("🌑 " if IS_WINDOWS else "") + "Detect Dark Photos", DarkImageDetectionApp, '#64748b')
    ]

    for text, cls, color in apps:
        tk.Button(btn_frame, text=text, font=btn_font, command=lambda c=cls: launch_tool(c),
                 bg=color, fg='white', activebackground=color, activeforeground='white',
                 bd=0, relief=tk.FLAT, cursor="hand2", pady=12).pack(pady=8, fill=tk.X)

    print("PhotoSift is ready.")
    root.mainloop()

if __name__ == "__main__":
    # multiprocessing.freeze_support() only on Windows
    if platform.system() == "Windows":
        import multiprocessing
        multiprocessing.freeze_support()
    main()
