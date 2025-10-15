"""
PhotoSift Application Launcher
Simple launcher to start PhotoSift applications
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading
import math
import sys
import os
import traceback
import logging

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# CRITICAL FIX: Setup Python path for imports
# This is essential for PyInstaller packaged executables
try:
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        application_path = sys._MEIPASS
        logger.info(f"Running as frozen executable. Base path: {application_path}")
    else:
        # Running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Running as script. Base path: {application_path}")
    
    # Add to sys.path if not already there
    if application_path not in sys.path:
        sys.path.insert(0, application_path)
        logger.info(f"Added {application_path} to sys.path")
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"sys.path: {sys.path[:3]}")
    
except Exception as e:
    print(f"ERROR: Failed to setup application path: {e}")
    traceback.print_exc()

class StartupSplash:
    """Animated startup splash screen for PhotoSift applications"""
    
    def __init__(self, app_title="PhotoSift", app_subtitle="Loading..."):
        self.app_title = app_title
        self.app_subtitle = app_subtitle
        self.root = None
        self.progress_label = None
        self.title_label = None
        self.progress_bar = None
        self.progress_canvas = None
        self.dot_label = None
        self.animation_running = True
        self.progress_value = 0
        self.loading_complete = False
        self.loading_error = None
        
    def show(self):
        """Display the animated startup splash screen"""
        try:
            self.root = tk.Tk()
            self.root.title("PhotoSift - Starting...")
            self.root.geometry("450x200")
            self.root.configure(bg='#1e293b')
            self.root.resizable(False, False)
            self.root.overrideredirect(True)  # Remove title bar
            
            # Center window
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
            y = (self.root.winfo_screenheight() // 2) - (200 // 2)
            self.root.geometry(f"450x200+{x}+{y}")
            
            # Create content frame
            main_frame = tk.Frame(self.root, bg='#1e293b', padx=30, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # App title (static, no animation)
            self.title_label = tk.Label(main_frame, 
                                       text=self.app_title, 
                                       font=("Segoe UI", 22, "bold"),
                                       bg='#1e293b', 
                                       fg='#3b82f6')  # Blue color for title
            self.title_label.pack(pady=(0, 5))
            
            # App subtitle
            subtitle_label = tk.Label(main_frame, 
                                     text=self.app_subtitle, 
                                     font=("Segoe UI", 12),
                                     bg='#1e293b', 
                                     fg='#94a3b8')
            subtitle_label.pack(pady=(0, 15))
            
            # Progress bar canvas
            self.progress_canvas = tk.Canvas(main_frame, 
                                           width=350, height=6, 
                                           bg='#334155', 
                                           highlightthickness=0,
                                           bd=0)
            self.progress_canvas.pack(pady=(0, 10))
            
            # Progress label with animated dots
            self.progress_label = tk.Label(main_frame, 
                                          text="Initializing", 
                                          font=("Segoe UI", 10),
                                          bg='#1e293b', 
                                          fg='#cbd5e1')
            self.progress_label.pack(pady=(0, 5))
            
            # Animated dots label
            self.dot_label = tk.Label(main_frame,
                                     text="...",
                                     font=("Segoe UI", 10),
                                     bg='#1e293b',
                                     fg='#3b82f6')
            self.dot_label.pack()
            
            self.root.update()
            
            # Start remaining animations
            self.start_dot_animation()
            
            logger.info("Splash screen created successfully")
            return self.root
            
        except Exception as e:
            logger.error(f"Error creating splash screen: {e}")
            traceback.print_exc()
            return None
    

    
    def start_dot_animation(self):
        """Animate pulsing dots for loading indicator"""
        dots = ["", ".", "..", "...", "..", "."]
        dot_index = 0
        
        def animate_step():
            nonlocal dot_index
            if self.animation_running and self.dot_label and self.root:
                try:
                    if self.root.winfo_exists():
                        self.dot_label.config(text=dots[dot_index])
                        dot_index = (dot_index + 1) % len(dots)
                        self.root.after(300, animate_step)  # Schedule next step in 300ms
                except tk.TclError:
                    # Window was destroyed
                    pass
                except Exception as e:
                    logger.error(f"Animation error: {e}")
        
        animate_step()
    
    def update_progress(self, message, progress_percent=None):
        """Update the progress message and bar"""
        if self.progress_label and self.root:
            try:
                if self.root.winfo_exists():
                    self.progress_label.config(text=message)
                    
                    # Update progress bar if percentage provided
                    if progress_percent is not None:
                        self.progress_value = progress_percent
                        self.animate_progress_bar()
                        
                    self.root.update()
            except tk.TclError:
                # Window was destroyed
                pass
            except Exception as e:
                logger.error(f"Progress update error: {e}")
    
    def animate_progress_bar(self):
        """Animate the progress bar to the current progress value"""
        if not self.progress_canvas or not self.root:
            return
            
        try:
            if not self.root.winfo_exists():
                return
                
            canvas_width = 350
            target_width = (self.progress_value / 100) * canvas_width
            current_width = getattr(self, '_current_progress_width', 0)
            step = max(1, (target_width - current_width) / 20)  # 20 animation steps
            
            def progress_step():
                nonlocal current_width
                if current_width < target_width and self.animation_running:
                    try:
                        if self.progress_canvas and self.root.winfo_exists():
                            # Clear and redraw
                            self.progress_canvas.delete("all")
                            
                            # Create progress bar
                            progress_color = "#3b82f6"  # Blue color
                            
                            self.progress_canvas.create_rectangle(0, 0, current_width, 6, 
                                                                fill=progress_color, 
                                                                outline=progress_color)
                            
                            current_width += step
                            self._current_progress_width = current_width
                            self.root.after(20, progress_step)  # Schedule next step in 20ms
                    except tk.TclError:
                        # Window was destroyed
                        pass
                    except Exception as e:
                        logger.error(f"Progress animation error: {e}")
            
            progress_step()
        except Exception as e:
            logger.error(f"Progress bar error: {e}")
    
    def close(self):
        """Close the splash screen and stop all animations"""
        self.animation_running = False
        logger.info("Closing splash screen")
        
        if self.root:
            try:
                # Simple fade out with null checks
                root_ref = self.root  # Keep a reference for the lambda functions
                
                def safe_fade(alpha_value):
                    try:
                        if root_ref and root_ref.winfo_exists():
                            root_ref.attributes('-alpha', alpha_value)
                    except:
                        pass
                
                def safe_destroy():
                    try:
                        if root_ref and root_ref.winfo_exists():
                            root_ref.quit()  # Exit mainloop first
                            root_ref.destroy()
                    except:
                        pass
                
                root_ref.attributes('-alpha', 0.8)
                root_ref.after(50, lambda: safe_fade(0.6))
                root_ref.after(100, lambda: safe_fade(0.4))
                root_ref.after(150, lambda: safe_fade(0.2))
                root_ref.after(200, safe_destroy)
                
            except Exception as e:
                logger.error(f"Error closing splash: {e}")
                try:
                    self.root.destroy()
                except:
                    pass
            
            self.root = None

def preload_models():
    """Preload all ImageClassification models with error handling"""
    
    splash = None
    try:
        logger.info("Starting model preload")
        # Show startup splash
        splash = StartupSplash("PhotoSift", "AI-Powered Image Management")
        root = splash.show()
        
        if not root:
            logger.error("Failed to create splash screen")
            return False
        
        # Track loading state
        loading_state = {
            'complete': False,
            'error': None,
            'current_progress': 0
        }
        
        def smooth_update_progress(message, target_percent, duration_ms=1000):
            """Smoothly animate progress to target percentage over duration"""
            try:
                current_percent = loading_state['current_progress']
                steps = max(1, duration_ms // 50)  # 50ms per step
                step_size = (target_percent - current_percent) / steps
                step_delay = duration_ms // steps
                
                def animate_step(step_count=0):
                    if step_count < steps and splash.root:
                        try:
                            new_percent = current_percent + (step_size * (step_count + 1))
                            splash.update_progress(message, min(target_percent, new_percent))
                            loading_state['current_progress'] = new_percent
                            splash.root.after(step_delay, lambda: animate_step(step_count + 1))
                        except:
                            pass
                    else:
                        loading_state['current_progress'] = target_percent
                
                animate_step()
            except Exception as e:
                logger.error(f"Progress update error: {e}")
        
        def load_models_thread():
            """Load all models in background thread with proper error handling"""
            try:
                logger.info("Loading models in background thread")
                
                # Step 1: Basic modules
                splash.root.after(0, lambda: splash.update_progress("Loading basic modules", 5))
                time.sleep(0.5)
                
                # Step 2: Image processing
                splash.root.after(0, lambda: smooth_update_progress("Loading image processing", 20, 800))
                time.sleep(0.8)
                
                try:
                    from PIL import Image, ImageTk
                    logger.info("PIL loaded successfully")
                except ImportError as e:
                    raise Exception(f"Failed to import PIL: {e}")
                
                # Step 3: AI models (heavy)
                splash.root.after(0, lambda: smooth_update_progress("Loading AI models", 40, 1000))
                time.sleep(1.0)
                
                # Import the heavy modules with error handling
                try:
                    from ImageClassification import classify_people_vs_screenshot, IMG_EXT
                    from ImageClassification import classify_people_vs_screenshot_batch
                    logger.info("ImageClassification loaded successfully")
                    splash.root.after(0, lambda: smooth_update_progress("Loading neural networks", 70, 1500))
                    time.sleep(1.5)
                except ImportError as e:
                    raise Exception(f"Failed to import ImageClassification: {e}")
                
                try:
                    from DuplicateImageIdentifier import get_clip_embedding_batch
                    logger.info("DuplicateImageIdentifier loaded successfully")
                    splash.root.after(0, lambda: smooth_update_progress("Finalizing", 90, 800))
                    time.sleep(0.8)
                except ImportError as e:
                    raise Exception(f"Failed to import DuplicateImageIdentifier: {e}")
                
                # Step 4: UI components
                try:
                    from CommonUI import ModernColors, ProgressWindow, ModernStyling
                    logger.info("CommonUI loaded successfully")
                    splash.root.after(0, lambda: smooth_update_progress("Ready!", 100, 500))
                    time.sleep(0.5)
                except ImportError as e:
                    raise Exception(f"Failed to import CommonUI: {e}")
                
                # Mark as complete
                loading_state['complete'] = True
                loading_state['error'] = None
                logger.info("All models loaded successfully")
                
                # Close splash after short delay
                splash.root.after(500, splash.close)
                
            except Exception as e:
                error_msg = f"Model loading failed: {str(e)}"
                logger.error(error_msg)
                traceback.print_exc()
                loading_state['error'] = error_msg
                loading_state['complete'] = False
                
                # Show error and close
                try:
                    splash.root.after(0, lambda: splash.update_progress(f"Error: {str(e)}", 0))
                    splash.root.after(3000, splash.close)
                except:
                    pass
        
        # Start loading in background thread
        loading_thread = threading.Thread(target=load_models_thread, daemon=True)
        loading_thread.start()
        logger.info("Loading thread started")
        
        # Run splash mainloop
        root.mainloop()
        
        # Wait for loading thread to complete (with timeout)
        loading_thread.join(timeout=30)
        
        # Check if loading was successful
        if loading_state['complete']:
            logger.info("\nModels loaded successfully!")
            splash.loading_complete = True
            
            # Now show app selection
            try:
                show_app_selection()
            except Exception as e:
                logger.error(f"Error showing app selection: {e}")
                traceback.print_exc()
            
            return True
        else:
            error_msg = loading_state['error'] or "Loading timed out or was cancelled"
            logger.error(f"\nModel loading failed: {error_msg}")
            splash.loading_complete = False
            
            # Show error dialog
            try:
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror(
                    "PhotoSift - Loading Error",
                    f"Failed to load required components:\n\n{error_msg}\n\n"
                    "Please check:\n"
                    "• All files are properly installed\n"
                    "• Required Python packages are available\n"
                    "• Sufficient system resources\n\n"
                    "Check the console output for more details."
                )
                error_root.destroy()
            except:
                pass
            
            return False
            
    except Exception as e:
        logger.error(f"Fatal error in preload_models: {e}")
        traceback.print_exc()
        
        # Show error dialog
        try:
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror(
                "PhotoSift - Fatal Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                "Please check the console output for more details."
            )
            error_root.destroy()
        except:
            pass
        
        return False
    finally:
        if splash and splash.root:
            try:
                splash.close()
            except:
                pass

def main():
    """Main launcher function"""
    print("PhotoSift Application Launcher")
    print("=" * 30)
    
    # Preload all models with smooth progress (handles its own main loop)
    print("Preloading AI models...")
    preload_models()  # This now includes the entire flow including app selection

def show_app_selection():
    """Show a selection window with two buttons to choose which app to launch"""
    
    # Create selection window
    selection_window = tk.Tk()
    selection_window.title("PhotoSift - Welcome! Please select a features")
    selection_window.geometry("500x300")  # Increased both width and height
    selection_window.configure(bg='#1e293b')
    selection_window.resizable(False, False)
    # Option: Minimal title bar with minimize button
    # selection_window.overrideredirect(True)  # Remove title bar (disabled for comparison)
    
    # Minimal title bar on Windows - removes maximize button, keeps minimize and close
    try:
        selection_window.attributes('-toolwindow', True)  # Minimal title bar on Windows
    except:
        pass  # Fallback for non-Windows systems
    
    # Center window
    selection_window.update_idletasks()
    x = (selection_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (selection_window.winfo_screenheight() // 2) - (300 // 2)
    selection_window.geometry(f"500x300+{x}+{y}")
    
    # Create main frame (also draggable)
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
        """Launch ImageClassifierGUI and destroy selection window"""
        selection_window.destroy()  # Completely destroy to avoid conflicts
        try:
            from ImageClassifierGUI import ImageClassifierApp
            # Create a new Tk instance
            app_root = tk.Tk()
            app = ImageClassifierApp(app_root)
            app_root.mainloop()
            # After app closes, show selection again
            show_app_selection()
        except Exception as e:
            print(f"Error launching ImageClassifierGUI: {e}")
            import traceback
            traceback.print_exc()
            show_app_selection()
    
    def launch_duplicate_finder():
        """Launch DuplicateImageIdentifierGUI and destroy selection window"""
        selection_window.destroy()  # Completely destroy to avoid conflicts
        try:
            from DuplicateImageIdentifierGUI import DuplicateImageIdentifierApp
            # Create a new Tk instance
            app_root = tk.Tk()
            app = DuplicateImageIdentifierApp(app_root)
            app_root.mainloop()
            # After app closes, show selection again
            show_app_selection()
        except Exception as e:
            print(f"Error launching DuplicateImageIdentifierGUI: {e}")
            import traceback
            traceback.print_exc()
            show_app_selection()

    def launch_blurry_detector():
        """Launch BlurryImageDetectionGUI and destroy selection window"""
        selection_window.destroy()  # Completely destroy to avoid conflicts
        try:
            from BlurryImageDetectionGUI import BlurryImageDetectionApp
            # Create a new Tk instance
            app_root = tk.Tk()
            app = BlurryImageDetectionApp(app_root)
            app_root.mainloop()
            # After app closes, show selection again
            show_app_selection()
        except Exception as e:
            print(f"Error launching BlurryImageDetectionGUI: {e}")
            import traceback
            traceback.print_exc()
            show_app_selection()
    
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

    # Identify blurry photo button
    blurry_btn = tk.Button(button_frame,
                             text="🌫️ Detect Blurry Photos",
                             command=launch_blurry_detector,
                             font=("Segoe UI", 12, "bold"),
                             bg='#f97316',  # Orange color
                             fg='#f1f5f9',
                             activebackground='#ea580c',
                             activeforeground='#f1f5f9',
                             bd=0, relief=tk.FLAT,
                             cursor="hand2",
                             padx=20, pady=5,
                             height=1)
    blurry_btn.pack(pady=5, fill=tk.X)
    
    # Ensure window is visible and on top
    selection_window.lift()
    selection_window.focus_force()
    selection_window.attributes('-topmost', True)
    selection_window.after(100, lambda: selection_window.attributes('-topmost', False))
    
    # Start the selection window
    selection_window.mainloop()



if __name__ == "__main__":
    main()