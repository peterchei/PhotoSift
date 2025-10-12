"""
Common UI components shared across PhotoSift applications.

This module contains reusable UI components that are used by multiple
applications within the PhotoSift suite, helping to maintain consistency
and reduce code duplication.
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import os
from PIL import Image, ImageTk


class ToolTip:
    """
    Create a tooltip for a given widget
    
    This class provides a reusable tooltip implementation that can be used
    across different PhotoSift applications. It shows helpful information
    when users hover over UI elements.
    
    Args:
        widget: The tkinter widget to attach the tooltip to
        text: The tooltip text to display
    """
    
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.widget.bind("<Motion>", self.motion)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def motion(self, event=None):
        self.unschedule()
        self.schedule()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        if self.tw:
            return
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        self.tw.configure(bg='#ffffe0', relief='solid', borderwidth=1)
        label = tk.Label(self.tw, text=self.text, justify=tk.LEFT,
                         background='#ffffe0', foreground='#000000',
                         relief='flat', borderwidth=0,
                         font=("Segoe UI", 10))
        label.pack(ipadx=8, ipady=4)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class ModernColors:
    """Centralized color scheme for PhotoSift applications"""
    
    @staticmethod
    def get_color_scheme():
        return {
            'bg_primary': '#1e293b',      # Dark blue background
            'bg_secondary': '#334155',    # Secondary dark blue
            'bg_card': '#475569',         # Card background
            'bg_sidebar': '#2d3748',      # Sidebar background
            'accent': '#3b82f6',          # Blue accent
            'accent_hover': '#2563eb',    # Blue hover
            'text_primary': '#f1f5f9',    # White text
            'text_secondary': '#94a3b8',  # Light gray text
            'success': '#10b981',         # Green
            'warning': '#f59e0b',         # Orange
            'danger': '#ef4444'           # Red
        }


class ProgressWindow:
    """Reusable progress window for long-running operations"""
    
    def __init__(self, parent, title="Processing", width=450, height=180):
        self.parent = parent
        self.colors = ModernColors.get_color_scheme()
        self.progress_window = None
        self.progress_var = None
        self.progress_label = None
        self.progress_detail = None
        self.progress_bar = None
        
        self.title = title
        self.width = width
        self.height = height
    
    def show(self, total, initial_text="Initializing..."):
        """Show the progress window"""
        if self.progress_window:
            return
            
        self.progress_window = tk.Toplevel(self.parent)
        self.progress_window.title(self.title)
        self.progress_window.geometry(f"{self.width}x{self.height}")
        self.progress_window.transient(self.parent)
        self.progress_window.grab_set()
        
        # Center the window
        self._center_window()
        
        # Style the window
        self.progress_window.configure(bg=self.colors['bg_primary'])
        frame = tk.Frame(self.progress_window, bg=self.colors['bg_primary'], padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress label
        self.progress_label = tk.Label(frame, 
                                      text=initial_text, 
                                      font=("Segoe UI", 13, "bold"), 
                                      bg=self.colors['bg_primary'],
                                      fg=self.colors['text_primary'])
        self.progress_label.pack(pady=(0, 15))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.configure("Modern.Horizontal.TProgressbar", 
                       thickness=20, 
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_secondary'],
                       borderwidth=0)
        
        self.progress_bar = ttk.Progressbar(frame, 
                                          style="Modern.Horizontal.TProgressbar", 
                                          length=390, mode='determinate', 
                                          maximum=total, variable=self.progress_var)
        self.progress_bar.pack(pady=(0, 15))
        
        # Detail label
        self.progress_detail = tk.Label(frame, 
                                       text="", 
                                       font=("Segoe UI", 11), 
                                       bg=self.colors['bg_primary'], 
                                       fg=self.colors['text_secondary'])
        self.progress_detail.pack()
    
    def update(self, current, total, status_text, detail_text=""):
        """Update progress window"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_var.set(current)
            self.progress_label.config(text=status_text)
            if detail_text:
                self.progress_detail.config(text=detail_text)
            self.progress_window.update_idletasks()
    
    def close(self):
        """Close the progress window"""
        if self.progress_window and self.progress_window.winfo_exists():
            self.progress_window.destroy()
            self.progress_window = None
    
    def _center_window(self):
        """Center the progress window on screen"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.progress_window.geometry(f"{self.width}x{self.height}+{x}+{y}")


class ModernStyling:
    """Centralized TTK styling for PhotoSift applications"""
    
    @staticmethod
    def apply_modern_styling(colors):
        """Apply modern dark theme styling to TTK widgets"""
        style = ttk.Style()
        
        # Set modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Tree styling
        style.configure("Modern.Treeview",
                       rowheight=28,
                       fieldbackground=colors['bg_card'],
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       selectbackground=colors['accent'],
                       selectforeground=colors['text_primary'],
                       borderwidth=0,
                       relief="flat")
        
        style.map("Modern.Treeview",
                 background=[('selected', colors['accent']),
                           ('active', colors['bg_secondary'])],
                 foreground=[('selected', colors['text_primary']),
                           ('active', colors['text_primary'])])
        
        # Scrollbar styling
        style.configure("Modern.Vertical.TScrollbar",
                       background=colors['bg_secondary'],
                       troughcolor=colors['bg_primary'],
                       borderwidth=0,
                       arrowcolor=colors['text_secondary'],
                       darkcolor=colors['bg_secondary'],
                       lightcolor=colors['bg_secondary'])
        
        style.configure("Modern.Horizontal.TScrollbar",
                       background=colors['bg_secondary'],
                       troughcolor=colors['bg_primary'],
                       borderwidth=0,
                       arrowcolor=colors['text_secondary'],
                       darkcolor=colors['bg_secondary'],
                       lightcolor=colors['bg_secondary'])


class StatusBar:
    """Reusable status bar component"""
    
    def __init__(self, parent, colors, initial_text="Ready"):
        self.parent = parent
        self.colors = colors
        
        # Create status bar frame
        self.status_frame = tk.Frame(parent, bg=colors['bg_secondary'], height=35)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame.pack_propagate(False)
        
        # Status variable and label
        self.status_var = tk.StringVar()
        self.status_var.set(initial_text)
        self.status_label = tk.Label(self.status_frame, 
                                   textvariable=self.status_var, 
                                   bd=0, relief=tk.FLAT, anchor=tk.W, 
                                   bg=colors['bg_secondary'], 
                                   fg=colors['text_secondary'], 
                                   font=("Segoe UI", 11))
        self.status_label.pack(fill=tk.BOTH, expand=True, padx=20)
    
    def set_text(self, text):
        """Update status bar text"""
        self.status_var.set(text)
    
    def set_color(self, bg_color, fg_color):
        """Update status bar colors"""
        self.status_label.config(bg=bg_color, fg=fg_color)


class ZoomControls:
    """Reusable zoom controls component"""
    
    def __init__(self, parent, colors, zoom_in_callback, zoom_out_callback):
        self.parent = parent
        self.colors = colors
        self.zoom_in_callback = zoom_in_callback
        self.zoom_out_callback = zoom_out_callback
        
        # Create zoom frame
        self.zoom_frame = tk.Frame(parent, bg=colors['bg_primary'])
        
        # Zoom out button
        self.zoom_out_btn = tk.Button(self.zoom_frame, 
                                     text="🔍-", 
                                     command=zoom_out_callback,
                                     font=("Segoe UI", 14),
                                     bg=colors['bg_secondary'],
                                     fg=colors['text_primary'],
                                     activebackground=colors['bg_card'],
                                     bd=0, relief=tk.FLAT, cursor="hand2",
                                     padx=12, pady=8)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Zoom in button
        self.zoom_in_btn = tk.Button(self.zoom_frame, 
                                    text="🔍+", 
                                    command=zoom_in_callback,
                                    font=("Segoe UI", 14),
                                    bg=colors['bg_secondary'],
                                    fg=colors['text_primary'],
                                    activebackground=colors['bg_card'],
                                    bd=0, relief=tk.FLAT, cursor="hand2",
                                    padx=12, pady=8)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Zoom percentage label
        self.zoom_label = tk.Label(self.zoom_frame, 
                                  text="100%", 
                                  font=("Segoe UI", 12), 
                                  bg=colors['bg_primary'], 
                                  fg=colors['text_secondary'])
        self.zoom_label.pack(side=tk.LEFT, fill=tk.Y)
    
    def pack(self, **kwargs):
        """Pack the zoom controls frame"""
        self.zoom_frame.pack(**kwargs)
    
    def update_controls(self, can_zoom_in, can_zoom_out, zoom_percentage):
        """Update zoom button states and percentage"""
        self.zoom_in_btn.config(state=tk.NORMAL if can_zoom_in else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if can_zoom_out else tk.DISABLED)
        self.zoom_label.config(text=f"{zoom_percentage}%")


class ModernButton:
    """Factory for creating consistently styled modern buttons"""
    
    @staticmethod
    def create_primary_button(parent, text, command, colors, **kwargs):
        """Create a primary accent button"""
        return tk.Button(parent, 
                        text=text, 
                        command=command,
                        font=("Segoe UI", 12, "bold"),
                        bg=colors['accent'],
                        fg=colors['text_primary'],
                        activebackground='#2563eb',
                        activeforeground=colors['text_primary'],
                        bd=0, relief=tk.FLAT, cursor="hand2",
                        padx=16, pady=8,
                        **kwargs)
    
    @staticmethod
    def create_danger_button(parent, text, command, colors, **kwargs):
        """Create a danger/delete button"""
        return tk.Button(parent, 
                        text=text, 
                        command=command,
                        font=("Segoe UI", 12, "bold"),
                        bg=colors['danger'],
                        fg=colors['text_primary'],
                        activebackground='#dc2626',
                        activeforeground=colors['text_primary'],
                        bd=0, relief=tk.FLAT, cursor="hand2",
                        padx=16, pady=8,
                        **kwargs)
    
    @staticmethod
    def create_secondary_button(parent, text, command, colors, **kwargs):
        """Create a secondary button"""
        return tk.Button(parent, 
                        text=text, 
                        command=command,
                        font=("Segoe UI", 12, "bold"),
                        bg=colors['bg_secondary'],
                        fg=colors['text_primary'],
                        activebackground=colors['bg_card'],
                        activeforeground=colors['text_primary'],
                        bd=0, relief=tk.FLAT, cursor="hand2",
                        padx=15, pady=8,
                        **kwargs)


class ImageUtils:
    """Utility functions for image operations"""
    
    # Class variable to track the current image window
    _current_image_window = None
    
    @staticmethod
    def open_full_image(parent_window, img_path):
        """
        Open an image in a reusable window at full size with detailed information
        
        This function reuses the same window for viewing images to prevent
        multiple image windows from accumulating. If a window is already open,
        it will be reused and updated with the new image content.
        
        Displays comprehensive image information including:
        - Full file path
        - File size
        - Image dimensions
        - Format and color mode
        - EXIF data (if available)
        
        Args:
            parent_window: The parent tkinter window
            img_path: Path to the image file
        """
        try:
            # Check if we already have an image window open
            if ImageUtils._current_image_window and ImageUtils._current_image_window.winfo_exists():
                # Reuse existing window
                top = ImageUtils._current_image_window
                top.title(f"PhotoSift - {os.path.basename(img_path)}")
                
                # Clear existing content
                for widget in top.winfo_children():
                    widget.destroy()
            else:
                # Create new window
                top = tk.Toplevel(parent_window)
                top.title(f"PhotoSift - {os.path.basename(img_path)}")
                ImageUtils._current_image_window = top
                
                # Set cleanup when window is closed
                def on_window_close():
                    ImageUtils._current_image_window = None
                    top.destroy()
                
                top.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Set window icon and properties
            top.resizable(True, True)
            
            # Bring window to front
            top.lift()
            top.focus_set()
            
            # Get colors for styling
            colors = ModernColors.get_color_scheme()
            
            # Create main container with info panel at top
            main_container = tk.Frame(top, bg=colors['bg_primary'])
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Info panel at top
            info_panel = tk.Frame(main_container, bg=colors['bg_secondary'], height=60)
            info_panel.pack(fill=tk.X, side=tk.TOP)
            info_panel.pack_propagate(False)
            
            # Load and display image
            img = Image.open(img_path)
            
            # Gather file information
            file_size = os.path.getsize(img_path)
            file_size_mb = file_size / (1024 * 1024)
            file_size_str = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size / 1024:.2f} KB"
            
            # Create info text with file details
            info_lines = []
            info_lines.append(f"📁 Path: {img_path}")
            info_lines.append(f"📏 Size: {img.width} × {img.height} pixels  |  💾 File: {file_size_str}  |  🎨 Format: {img.format}  |  Mode: {img.mode}")
            
            # Extract EXIF data if available
            exif_data = {}
            try:
                exif = img._getexif()
                if exif:
                    from PIL.ExifTags import TAGS, GPSTAGS
                    
                    # Map EXIF tag IDs to names
                    for tag_id, value in exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        exif_data[tag_name] = value
                    
                    # Build EXIF info line
                    exif_parts = []
                    
                    # Camera make and model
                    if 'Make' in exif_data and 'Model' in exif_data:
                        camera = f"{exif_data['Make']} {exif_data['Model']}".strip()
                        exif_parts.append(f"📷 {camera}")
                    elif 'Model' in exif_data:
                        exif_parts.append(f"📷 {exif_data['Model']}")
                    
                    # Date taken
                    if 'DateTimeOriginal' in exif_data:
                        exif_parts.append(f"📅 {exif_data['DateTimeOriginal']}")
                    elif 'DateTime' in exif_data:
                        exif_parts.append(f"📅 {exif_data['DateTime']}")
                    
                    # Exposure settings
                    exposure_parts = []
                    if 'FNumber' in exif_data:
                        f_num = exif_data['FNumber']
                        if isinstance(f_num, tuple):
                            f_val = f_num[0] / f_num[1] if f_num[1] != 0 else f_num[0]
                        else:
                            f_val = f_num
                        exposure_parts.append(f"f/{f_val:.1f}")
                    
                    if 'ExposureTime' in exif_data:
                        exp_time = exif_data['ExposureTime']
                        if isinstance(exp_time, tuple):
                            exp_str = f"{exp_time[0]}/{exp_time[1]}s" if exp_time[1] != 1 else f"{exp_time[0]}s"
                        else:
                            exp_str = f"{exp_time}s"
                        exposure_parts.append(exp_str)
                    
                    if 'ISOSpeedRatings' in exif_data:
                        exposure_parts.append(f"ISO {exif_data['ISOSpeedRatings']}")
                    
                    if 'FocalLength' in exif_data:
                        focal = exif_data['FocalLength']
                        if isinstance(focal, tuple):
                            focal_val = focal[0] / focal[1] if focal[1] != 0 else focal[0]
                        else:
                            focal_val = focal
                        exposure_parts.append(f"{focal_val:.0f}mm")
                    
                    if exposure_parts:
                        exif_parts.append("  |  ".join(exposure_parts))
                    
                    # GPS location
                    if 'GPSInfo' in exif_data:
                        exif_parts.append("📍 GPS Data Available")
                    
                    if exif_parts:
                        info_lines.append("  |  ".join(exif_parts))
                        
            except (AttributeError, KeyError, IndexError, TypeError):
                # No EXIF data or error reading it
                pass
            
            # Display info in panel
            info_text = tk.Text(info_panel, 
                              height=len(info_lines),
                              bg=colors['bg_secondary'],
                              fg=colors['text_primary'],
                              font=("Consolas", 9),
                              wrap=tk.WORD,
                              bd=0,
                              padx=15,
                              pady=10,
                              relief=tk.FLAT,
                              cursor="arrow")
            info_text.pack(fill=tk.BOTH, expand=True)
            
            # Insert info text
            for line in info_lines:
                info_text.insert(tk.END, line + "\n")
            
            info_text.config(state=tk.DISABLED)  # Make read-only
            
            # Add selection and copy capability
            def copy_path_to_clipboard(event=None):
                top.clipboard_clear()
                top.clipboard_append(img_path)
                # Brief visual feedback
                info_text.config(bg=colors['accent'])
                top.after(200, lambda: info_text.config(bg=colors['bg_secondary']))
            
            info_text.bind('<Control-c>', copy_path_to_clipboard)
            
            # Add tooltip
            ToolTip(info_text, "Ctrl+C to copy file path to clipboard")
            # Add tooltip
            ToolTip(info_text, "Ctrl+C to copy file path to clipboard")
            
            # Get screen dimensions to limit image size if needed
            screen_width = top.winfo_screenwidth()
            screen_height = top.winfo_screenheight()
            
            # Calculate max size (90% of screen, accounting for info panel)
            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9) - 120  # Reserve space for info panel
            
            # Resize if image is too large for screen
            display_img = img.copy()
            if display_img.width > max_width or display_img.height > max_height:
                display_img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(display_img)
            
            # Create scrollable frame for large images
            frame = tk.Frame(main_container, bg='black')
            frame.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
            
            canvas = tk.Canvas(frame, bg='black')
            v_scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
            
            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack scrollbars and canvas
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Create image label
            lbl = tk.Label(canvas, image=img_tk, bg='black')
            lbl.image = img_tk  # Keep reference
            
            # Add image to canvas
            canvas.create_window((0, 0), window=lbl, anchor=tk.NW)
            
            # Configure scroll region
            lbl.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Center the window
            window_width = min(display_img.width + 50, max_width)
            window_height = min(display_img.height + 170, int(screen_height * 0.9))  # Account for info panel
            
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            top.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Add keyboard shortcuts
            def on_escape(event):
                ImageUtils._current_image_window = None
                top.destroy()
            
            def on_space(event):
                ImageUtils._current_image_window = None
                top.destroy()
            
            top.bind('<Escape>', on_escape)
            top.bind('<space>', on_space)
            
            # Double-click to close window
            def on_double_click(event):
                ImageUtils._current_image_window = None
                top.destroy()
            
            lbl.bind('<Double-Button-1>', on_double_click)
            canvas.bind('<Double-Button-1>', on_double_click)
            
            # Mouse wheel scrolling
            def on_mousewheel(event):
                if event.state == 0:  # No modifier keys
                    canvas.yview_scroll(-1 * (event.delta // 120), "units")
                elif event.state == 1:  # Shift key
                    canvas.xview_scroll(-1 * (event.delta // 120), "units")
            
            canvas.bind("<MouseWheel>", on_mousewheel)
            
        except Exception as e:
            # Show error dialog if image can't be opened
            tkinter.messagebox.showerror(
                "Error Opening Image", 
                f"Could not open image:\n{img_path}\n\nError: {str(e)}"
            )


class TrashManager:
    """
    Manages trash functionality for PhotoSift applications.
    
    This class provides a unified interface for trash operations including
    counting files in trash, updating trash button display, and opening
    the trash folder. It can be used by both ImageClassifierGUI and
    DuplicateImageIdentifierGUI to avoid code duplication.
    """
    
    def __init__(self, parent_frame, colors, folder_callback, img_extensions, button_style="emoji"):
        """
        Initialize TrashManager
        
        Args:
            parent_frame: The parent frame to add the trash button to
            colors: Color scheme dictionary
            folder_callback: Function that returns the current folder path
            img_extensions: Set/list of supported image file extensions (e.g., IMG_EXT)
            button_style: "emoji" for 🗑️ style, "text" for "Trash" style
        """
        self.parent_frame = parent_frame
        self.colors = colors
        self.folder_callback = folder_callback
        self.img_extensions = img_extensions
        self.button_style = button_style
        
        # Create trash button and variable
        self.trash_btn_var = tk.StringVar(value=self._get_initial_text())
        self.trash_btn = self._create_trash_button()
        
    def _get_initial_text(self):
        """Get initial button text based on style"""
        return "🗑️ 0" if self.button_style == "emoji" else "Trash (0)"
    
    def _create_trash_button(self):
        """Create the trash button using ModernButton"""
        return ModernButton.create_secondary_button(
            self.parent_frame, "", self.open_trash_folder, self.colors,
            textvariable=self.trash_btn_var)
    
    def pack(self, **kwargs):
        """Pack the trash button with given arguments"""
        self.trash_btn.pack(**kwargs)
        
    def get_current_folder(self):
        """Get the current folder from the callback"""
        return self.folder_callback()
    
    def update_trash_count(self):
        """Update trash button with count of files in trash directory"""
        folder = self.get_current_folder()
        if folder:
            trash_path = os.path.join(folder, "Trash")
            if os.path.exists(trash_path):
                # Count image files in trash
                count = sum(1 for f in os.listdir(trash_path) 
                         if os.path.isfile(os.path.join(trash_path, f)) 
                         and os.path.splitext(f)[1].lower() in self.img_extensions)
                
                if self.button_style == "emoji":
                    self.trash_btn_var.set(f"🗑️ {count}")
                else:
                    self.trash_btn_var.set(f"Trash ({count})")
            else:
                self.trash_btn_var.set(self._get_initial_text())
        else:
            self.trash_btn_var.set(self._get_initial_text())

    def open_trash_folder(self):
        """Open the local Trash folder in the selected directory"""
        folder = self.get_current_folder()
        if not folder:
            tk.messagebox.showinfo("No Folder", "Please select a folder first to locate the Trash directory.")
            return
            
        trash_dir = os.path.join(folder, "Trash")
        
        if os.path.exists(trash_dir):
            # Open folder in Windows Explorer
            os.startfile(trash_dir)
        else:
            if self.button_style == "emoji":
                tk.messagebox.showinfo("Trash Empty", f"No Trash folder found at:\n{trash_dir}\n\nNo items have been cleaned yet.")
            else:
                tk.messagebox.showinfo("Trash Folder", "Trash folder does not exist yet.")