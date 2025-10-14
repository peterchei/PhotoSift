"""
PhotoSift Application Launcher
Simple launcher to start PhotoSift applications
"""

import tkinter as tk
import time
import threading
import math

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
        
    def show(self):
        """Display the animated startup splash screen"""
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
        
        return self.root
    

    
    def start_dot_animation(self):
        """Animate pulsing dots for loading indicator"""
        dots = ["", ".", "..", "...", "..", "."]
        dot_index = 0
        
        def animate_step():
            nonlocal dot_index
            if self.animation_running and self.dot_label:
                try:
                    self.dot_label.config(text=dots[dot_index])
                    dot_index = (dot_index + 1) % len(dots)
                    self.root.after(300, animate_step)  # Schedule next step in 300ms
                except:
                    pass
        
        animate_step()
    
    def update_progress(self, message, progress_percent=None):
        """Update the progress message and bar"""
        if self.progress_label and self.root:
            try:
                self.progress_label.config(text=message)
                
                # Update progress bar if percentage provided
                if progress_percent is not None:
                    self.progress_value = progress_percent
                    self.animate_progress_bar()
                    
                self.root.update()
            except:
                pass
    
    def animate_progress_bar(self):
        """Animate the progress bar to the current progress value"""
        if not self.progress_canvas:
            return
            
        canvas_width = 350
        target_width = (self.progress_value / 100) * canvas_width
        current_width = getattr(self, '_current_progress_width', 0)
        step = max(1, (target_width - current_width) / 20)  # 20 animation steps
        
        def progress_step():
            nonlocal current_width
            if current_width < target_width and self.animation_running and self.progress_canvas:
                try:
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
                except:
                    pass
        
        progress_step()
    
    def close(self):
        """Close the splash screen and stop all animations"""
        self.animation_running = False
        
        if self.root:
            try:
                # Simple fade out with null checks
                root_ref = self.root  # Keep a reference for the lambda functions
                
                def safe_fade(alpha_value):
                    if root_ref and root_ref.winfo_exists():
                        try:
                            root_ref.attributes('-alpha', alpha_value)
                        except:
                            pass
                
                def safe_destroy():
                    if root_ref and root_ref.winfo_exists():
                        try:
                            root_ref.destroy()
                        except:
                            pass
                
                root_ref.attributes('-alpha', 0.8)
                root_ref.after(50, lambda: safe_fade(0.6))
                root_ref.after(100, lambda: safe_fade(0.4))
                root_ref.after(150, lambda: safe_fade(0.2))
                root_ref.after(200, safe_destroy)
                
            except:
                try:
                    self.root.destroy()
                except:
                    pass
            
            self.root = None

def preload_models():
    """Preload all ImageClassification models with smooth progress updates"""
    
    # Show startup splash
    splash = StartupSplash("PhotoSift", "AI-Powered Image Management")
    splash.show()
    
    def smooth_update_progress(message, target_percent, duration_ms=1000):
        """Smoothly animate progress to target percentage over duration"""
        current_percent = getattr(splash, 'current_progress', 0)
        steps = max(1, duration_ms // 50)  # 50ms per step
        step_size = (target_percent - current_percent) / steps
        step_delay = duration_ms // steps
        
        def animate_step(step_count=0):
            if step_count < steps:
                new_percent = current_percent + (step_size * (step_count + 1))
                splash.update_progress(message, min(target_percent, new_percent))
                splash.current_progress = new_percent
                splash.root.after(step_delay, lambda: animate_step(step_count + 1))
            else:
                splash.current_progress = target_percent
                
        animate_step()
    
    def load_with_progress():
        """Load models with real-time progress updates"""
        try:
            # Step 1: Load basic modules
            splash.update_progress("Loading basic modules", 5)
            splash.root.update()
            
            # Simulate smooth progress to 15%
            smooth_update_progress("Loading basic modules", 15, 800)
            splash.root.after(900, lambda: load_step_2())
            
        except Exception as e:
            splash.update_progress(f"Error: {str(e)}", 0)
            splash.root.after(3000, splash.close)
    
    def load_step_2():
        try:
            import os
            import sys
            
            # Step 2: Load PIL and image processing
            smooth_update_progress("Loading image processing libraries", 30, 1000)
            splash.root.after(1100, lambda: load_step_3())
            
        except Exception as e:
            splash.update_progress(f"Error: {str(e)}", 0)
            splash.root.after(3000, splash.close)
    
    def load_step_3():
        try:
            from PIL import Image, ImageTk
            
            # Step 3: Start loading AI models (heavy operation)
            smooth_update_progress("Loading AI models (this may take a moment)", 45, 800)
            splash.root.after(900, lambda: load_heavy_models())
            
        except Exception as e:
            splash.update_progress(f"Error: {str(e)}", 0)
            splash.root.after(3000, splash.close)
    
    def load_heavy_models():
        """Load heavy AI models with progress simulation"""
        try:
            # Simulate progress while loading heavy models
            splash.update_progress("Initializing neural networks", 50)
            
            def progress_simulation(current=50):
                if current < 75:
                    # Simulate gradual loading
                    splash.update_progress("Initializing neural networks", current)
                    next_progress = current + 2
                    splash.root.after(200, lambda: progress_simulation(next_progress))
                else:
                    # Actually load the models now
                    load_actual_models()
            
            progress_simulation()
            
        except Exception as e:
            splash.update_progress(f"Error: {str(e)}", 0)
            splash.root.after(3000, splash.close)
    
    def load_actual_models():
        """Load the actual heavy models"""
        def do_heavy_import():
            try:
                # This will block, but progress bar is already at 75%
                from ImageClassification import classify_people_vs_screenshot, IMG_EXT
                from ImageClassification import classify_people_vs_screenshot_batch
                from DuplicateImageIdentifier import get_clip_embedding_batch
                splash.root.after(0, lambda: finalize_loading())
            except Exception as e:
                splash.root.after(0, lambda: handle_error(str(e)))
        
        # Run heavy import in thread to avoid blocking GUI
        threading.Thread(target=do_heavy_import, daemon=True).start()
        
        # Continue progress animation while loading
        def animate_loading(current=75):
            if current < 85:
                splash.update_progress("Loading neural networks", current)
                splash.root.after(300, lambda: animate_loading(current + 1))
        
        animate_loading()
    
    def finalize_loading():
        try:
            # Step 4: Load other components
            smooth_update_progress("Loading PhotoSift components", 95, 600)
            splash.root.after(700, lambda: load_final_step())
            
        except Exception as e:
            handle_error(str(e))
    
    def load_final_step():
        try:
            from CommonUI import ModernColors, ProgressWindow, ModernStyling
            
            # Step 5: Finalize
            smooth_update_progress("Ready to launch!", 100, 800)
            splash.root.after(1200, lambda: complete_loading())
            
        except Exception as e:
            handle_error(str(e))
    
    def complete_loading():
        print("All models loaded successfully!")
        # Set a flag to indicate loading is complete
        splash.loading_complete = True
        splash.update_progress("Ready to launch!", 100)
        
        # Close after a short delay
        splash.root.after(500, splash.close)
    
    def handle_error(error_msg):
        splash.update_progress(f"Error loading models: {error_msg}", 0)
        print(f"Error loading models: {error_msg}")
        splash.root.after(3000, splash.close)
    
    # Initialize progress tracking
    splash.current_progress = 0
    splash.loading_complete = False
    
    # Start loading process
    splash.root.after(100, load_with_progress)
    
    # Run the splash window main loop
    splash.root.mainloop()
    
    # After splash closes, check if loading was successful and show selection
    if getattr(splash, 'loading_complete', False):
        print("\nModels loaded! PhotoSift is ready.")
        show_app_selection()
    else:
        print("Loading was cancelled or failed.")
        return False
    
    return True

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