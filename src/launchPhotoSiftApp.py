"""
PhotoSift Application Launcher
Linux Stability Optimized Version
"""

import os, sys, time, logging, multiprocessing

# Configure logging
log_dir = os.path.join(os.path.expanduser('~'), 'PhotoSift', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'photosift_app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file, encoding='utf-8')]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("PhotoSift Starting (Stability Mode)...")
    
    # Setup path
    application_path = os.path.dirname(os.path.abspath(__file__))
    if application_path not in sys.path:
        sys.path.insert(0, application_path)

    # 1. UI Initialization
    import tkinter as tk
    root = tk.Tk()
    root.title("PhotoSift")
    root.geometry("500x550")
    root.configure(bg='#1e293b')
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (550 // 2)
    root.geometry(f"+{x}+{y}")
    root.update()

    # 2. Lazy Imports
    try:
        logger.info("Loading AI modules (Pillow, Torch, Transformers)...")
        from PIL import Image, ImageTk
        import torch
        import cv2
        from transformers import CLIPModel, CLIPProcessor
        
        logger.info("Loading Application logic...")
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
        logger.error(f"Initialization failed: {e}")
        import traceback
        messagebox.showerror("Startup Error", f"Failed to load PhotoSift: {e}")
        return

    # 3. Build Selection Menu
    logger.info("Building selection menu...")
    
    # Title
    tk.Label(root, text="PhotoSift", font=("Segoe UI", 26, "bold"), 
             bg='#1e293b', fg='#3b82f6').pack(pady=(40, 10))
    
    tk.Label(root, text="AI-Powered Image Management", font=("Segoe UI", 12), 
             bg='#1e293b', fg='#94a3b8').pack(pady=(0, 30))
    
    btn_frame = tk.Frame(root, bg='#1e293b')
    btn_frame.pack(fill=tk.X, padx=60)

    def launch_tool(cls):
        # Create toplevel for the tool
        tool_win = tk.Toplevel(root)
        # Attempt to set icon for tool window
        try:
            icon_path = os.path.join(os.path.dirname(application_path), "resources", "app.ico")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                icon_img = ImageTk.PhotoImage(img.resize((32, 32)))
                tool_win.wm_iconphoto(True, icon_img)
                tool_win._icon = icon_img
        except: pass
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
                 activebackground=color, activeforeground='white',
                 bd=0, relief=tk.FLAT, cursor="hand2", pady=12).pack(pady=8, fill=tk.X)
        root.update()

    # Final safe icon set for root
    try:
        icon_path = os.path.join(os.path.dirname(application_path), "resources", "app.ico")
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            icon_img = ImageTk.PhotoImage(img.resize((32, 32)))
            root.wm_iconphoto(True, icon_img)
            root._icon = icon_img
    except: pass

    logger.info("PhotoSift is ready.")
    root.mainloop()

if __name__ == "__main__":
    # Note: freeze_support() is only needed for PyInstaller on Windows
    if sys.platform == 'win32':
        multiprocessing.freeze_support()
    main()
