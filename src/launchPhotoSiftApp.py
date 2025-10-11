"""
PhotoSift Application Launcher
Simple launcher to start PhotoSift applications
"""

import tkinter as tk
import time
import threading

class StartupSplash:
    """Simple startup splash screen for PhotoSift applications"""
    
    def __init__(self, app_title="PhotoSift", app_subtitle="Loading..."):
        self.app_title = app_title
        self.app_subtitle = app_subtitle
        self.root = None
        self.progress_label = None
        
    def show(self):
        """Display the startup splash screen"""
        self.root = tk.Tk()
        self.root.title("PhotoSift - Starting...")
        self.root.geometry("400x150")
        self.root.configure(bg='#1e293b')
        self.root.resizable(False, False)
        self.root.overrideredirect(True)  # Remove title bar
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (150 // 2)
        self.root.geometry(f"400x150+{x}+{y}")
        
        # Create content frame
        main_frame = tk.Frame(self.root, bg='#1e293b', padx=30, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # App title
        title_label = tk.Label(main_frame, 
                              text=self.app_title, 
                              font=("Segoe UI", 20, "bold"),
                              bg='#1e293b', 
                              fg='#f1f5f9')
        title_label.pack(pady=(0, 5))
        
        # App subtitle
        subtitle_label = tk.Label(main_frame, 
                                 text=self.app_subtitle, 
                                 font=("Segoe UI", 11),
                                 bg='#1e293b', 
                                 fg='#94a3b8')
        subtitle_label.pack(pady=(0, 15))
        
        # Progress label
        self.progress_label = tk.Label(main_frame, 
                                      text="Initializing...", 
                                      font=("Segoe UI", 10),
                                      bg='#1e293b', 
                                      fg='#cbd5e1')
        self.progress_label.pack()
        
        self.root.update()
        return self.root
    
    def update_progress(self, message):
        """Update the progress message"""
        if self.progress_label and self.root:
            try:
                self.progress_label.config(text=message)
                self.root.update()
            except:
                pass
    
    def close(self):
        """Close the splash screen"""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None

def preload_models():
    """Preload all ImageClassification models with progress updates"""
    
    # Show startup splash
    splash = StartupSplash("PhotoSift", "AI-Powered Image Management")
    splash.show()
    
    try:
        # Step 1: Load basic modules
        splash.update_progress("Loading basic modules...")
        time.sleep(0.5)
        import os
        import sys
        
        # Step 2: Load PIL and image processing
        splash.update_progress("Loading image processing libraries...")
        time.sleep(0.5)
        from PIL import Image, ImageTk
        
        # Step 3: Load TensorFlow and AI models (this is the slow part)
        splash.update_progress("Loading AI models (this may take a moment)...")
        time.sleep(1)  # Give user time to see the message
        
        # Import ImageClassification to trigger all model loading
        from ImageClassification import classify_people_vs_screenshot, IMG_EXT
        from ImageClassification import classify_people_vs_screenshot_batch
        
        # Step 4: Load other PhotoSift components
        splash.update_progress("Loading PhotoSift components...")
        time.sleep(0.5)
        from CommonUI import ModernColors, ProgressWindow, ModernStyling
        
        # Step 5: Finalize
        splash.update_progress("Ready!")
        time.sleep(1)
        
        print("All models loaded successfully!")
        return True
        
    except Exception as e:
        splash.update_progress(f"Error loading models: {str(e)}")
        time.sleep(3)
        print(f"Error loading models: {e}")
        return False
    
    finally:
        splash.close()

def main():
    """Main launcher function"""
    print("PhotoSift Application Launcher")
    print("=" * 30)
    
    # Preload all models first
    print("Preloading AI models...")
    success = preload_models()
    
    if not success:
        print("Failed to load models. Exiting.")
        return
    
    print("\nModels loaded! PhotoSift is ready.")

    # Show selection window to choose which app to launch
    show_app_selection()

def show_app_selection():
    """Show a selection window with two buttons to choose which app to launch"""
    
    # Create selection window
    selection_window = tk.Tk()
    selection_window.title("PhotoSift - Welcome! Please select a features")
    selection_window.geometry("500x250")  # Increased both width and height
    selection_window.configure(bg='#1e293b')
    selection_window.resizable(False, False)
    
    # Center window
    selection_window.update_idletasks()
    x = (selection_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (selection_window.winfo_screenheight() // 2) - (250 // 2)
    selection_window.geometry(f"500x250+{x}+{y}")
    
    # Create main frame
    main_frame = tk.Frame(selection_window, bg='#1e293b', padx=30, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # App title
    title_label = tk.Label(main_frame, 
                          text="PhotoSift", 
                          font=("Segoe UI", 22, "bold"),
                          bg='#1e293b', 
                          fg='#f1f5f9')
    title_label.pack(pady=(0, 5))
    
    # Subtitle
    subtitle_label = tk.Label(main_frame, 
                             text="Choose your image management tool", 
                             font=("Segoe UI", 11),
                             bg='#1e293b', 
                             fg='#94a3b8')
    subtitle_label.pack(pady=(0, 20))
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg='#1e293b')
    button_frame.pack(fill=tk.X, pady=5)
    
    def launch_classifier():
        """Launch ImageClassifierGUI and close selection window"""
        selection_window.destroy()
        try:
            from ImageClassifierGUI import ImageClassifierApp
            root = tk.Tk()
            app = ImageClassifierApp(root)
            root.mainloop()
        except Exception as e:
            print(f"Error launching ImageClassifierGUI: {e}")
    
    def launch_duplicate_finder():
        """Launch DuplicateImageIdentifierGUI and close selection window"""
        selection_window.destroy()
        try:
            from DuplicateImageIdentifierGUI import DuplicateImageIdentifierApp
            root = tk.Tk()
            app = DuplicateImageIdentifierApp(root)
            root.mainloop()
        except Exception as e:
            print(f"Error launching DuplicateImageIdentifierGUI: {e}")
    
    # Identify unwanted photo button
    unwanted_btn = tk.Button(button_frame,
                            text="🧹 Identify Unwanted Photos",
                            command=launch_classifier,
                            font=("Segoe UI", 12, "bold"),
                            bg='#3b82f6',
                            fg='#f1f5f9',
                            activebackground='#2563eb',
                            activeforeground='#f1f5f9',
                            bd=0, relief=tk.FLAT, 
                            cursor="hand2",
                            padx=20, pady=5,
                            height=1)
    unwanted_btn.pack(pady=5, fill=tk.X)
    
    # Identify duplicated photo button
    duplicate_btn = tk.Button(button_frame,
                             text="🔍 Identify Duplicate Photos", 
                             command=launch_duplicate_finder,
                             font=("Segoe UI", 12, "bold"),
                             bg='#10b981',
                             fg='#f1f5f9',
                             activebackground='#059669',
                             activeforeground='#f1f5f9',
                             bd=0, relief=tk.FLAT,
                             cursor="hand2", 
                             padx=20, pady=5,
                             height=1)
    duplicate_btn.pack(pady=5, fill=tk.X)
    
    # Start the selection window
    selection_window.mainloop()



if __name__ == "__main__":
    main()