"""
GUI for Blurry Image Detection
Provides a user interface to detect blurry images in a folder and manage them.
"""

# Standard library imports
import os
import threading
import shutil
from pathlib import Path

# Third-party imports
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Local imports
from BlurryImageDetection import detect_blurry_images_batch, get_recommended_threshold, BlurryImageDetector
from CommonUI import (ToolTip, ModernColors, ProgressWindow, ModernStyling,
                     StatusBar, ZoomControls, ModernButton, ImageUtils, TrashManager, FileOperations)

class BlurryImageDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoSift - Blurry Image Detector")
        # Maximize window on startup
        import sys
        if sys.platform.startswith('win'):
            try:
                self.root.state('zoomed')
            except: pass
        else:
            try:
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            except:
                pass
        
        self.folder = ""
        self.blurry_images = []
        self.sharp_images = []
        self.current_paths = []
        self.current_page = 0
        self.page_size = 50
        self.thumb_imgs = []
        self.image_cache = {}
        self.blur_scores = {}  # Cache blur scores to avoid recalculation
        self.selected_check_vars = []
        self._trash_icon_cache = {}  # Cache for trash icon sizes
        self._cleaning_in_progress = False
        self.detector = BlurryImageDetector()

        # Thumbnail size configuration
        self.thumb_size = (240, 180)  # Default size
        self.min_thumb_size = (60, 45)  # Minimum size
        self.max_thumb_size = (580, 360)  # Maximum size

        # Use centralized color scheme
        self.colors = ModernColors.get_color_scheme()

        # Initialize progress window
        self.progress_window = ProgressWindow(self.root, "Blurry Image Detection")

        self.setup_ui()

        # Apply modern styling using common component
        ModernStyling.apply_modern_styling(self.colors)

        # Apply dark theme after UI setup
        self.root.after(100, self.apply_dark_theme_fix)

    def apply_dark_theme_fix(self):
        """Ensure dark theme is properly applied to all components"""
        try:
            style = ttk.Style()
            treeview_config = {
                'fieldbackground': self.colors['bg_card'],
                'background': self.colors['bg_card'],
                'foreground': self.colors['text_primary'],
                'borderwidth': 0,
            }
            style.configure("Treeview", **treeview_config)
            style.map("Treeview",
                     background=[('selected', self.colors['accent']), ('active', self.colors['bg_secondary'])],
                     foreground=[('selected', self.colors['text_primary']), ('active', self.colors['text_primary'])])
            self.tree.configure(style="Treeview")
        except Exception as e:
            print(f"Error applying dark theme fix: {e}")

    def setup_ui(self):
        self.root.configure(bg=self.colors['bg_primary'])

        # Modern header
        header = tk.Frame(self.root, bg=self.colors['bg_primary'], height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 0))
        header.pack_propagate(False)

        # App title section
        title_frame = tk.Frame(header, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        title_label = tk.Label(title_frame,
                              text="PhotoSift",
                              font=("Segoe UI", 28, "bold"),
                              bg=self.colors['bg_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(title_frame,
                                 text="Blurry Image Detector",
                                 font=("Segoe UI", 14),
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor="w")

        # Header buttons frame
        header_buttons = tk.Frame(header, bg=self.colors['bg_primary'])
        header_buttons.pack(side=tk.RIGHT, fill=tk.Y)

        # Create trash manager using common component in header
        self.trash_manager = TrashManager(
            header_buttons,
            self.colors,
            lambda: self.folder,
            {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'},
            button_style="emoji")
        self.trash_manager.pack(side=tk.RIGHT, padx=(10, 0))

        # Main content container
        content = tk.Frame(self.root, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 20))

        # Left panel (sidebar) for controls and results
        left_panel = tk.Frame(content, width=300, bg=self.colors['bg_sidebar'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        # Right panel (main area) for thumbnails
        main_area = tk.Frame(content, bg=self.colors['bg_primary'])
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.right_frame = main_area

        # --- Left Panel ---
        # Folder selection
        folder_frame = tk.Frame(left_panel, bg=self.colors['bg_sidebar'])
        folder_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        btn_select = ModernButton.create_primary_button(folder_frame, text="Select Folder", command=self.select_folder, colors=self.colors)
        btn_select.pack(fill=tk.X)
        ToolTip(btn_select, "Select a folder to scan for blurry images")

        self.lbl_folder = tk.Label(folder_frame, text="No folder selected",
                                   wraplength=260, justify=tk.LEFT,
                                   bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                                   font=("Segoe UI", 10))
        self.lbl_folder.pack(fill=tk.X, pady=(8, 0))

        # Threshold control
        threshold_frame = tk.Frame(left_panel, bg=self.colors['bg_sidebar'])
        threshold_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(threshold_frame, text="Blur Threshold",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors['bg_sidebar'], fg=self.colors['text_primary']).pack(anchor="w")

        self.threshold_var = tk.DoubleVar(value=100.0)
        self.threshold_slider = ttk.Scale(threshold_frame, from_=10, to=300,
                                          orient=tk.HORIZONTAL, variable=self.threshold_var,
                                          command=self.update_threshold_label)
        self.threshold_slider.pack(fill=tk.X, pady=(5, 0))
        ToolTip(self.threshold_slider, "Adjust the sensitivity for blur detection.\nLower values detect only very blurry images.")

        self.lbl_threshold = tk.Label(threshold_frame, text="Current: 100.0",
                                      bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                                      font=("Segoe UI", 10))
        self.lbl_threshold.pack(anchor="w")

        # Scan button
        btn_scan = ModernButton.create_primary_button(left_panel, text="Start Scan", command=self.start_scan, colors=self.colors)
        btn_scan.pack(fill=tk.X, padx=20)
        ToolTip(btn_scan, "Begin scanning the selected folder for blurry images")

        # Results section
        categories_section = tk.Frame(left_panel, bg=self.colors['bg_sidebar'])
        categories_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        categories_label = tk.Label(categories_section,
                                   text="Categories",
                                   bg=self.colors['bg_sidebar'],
                                   font=("Segoe UI", 14, "bold"),
                                   fg=self.colors['text_primary'])
        categories_label.pack(anchor="w", pady=(0, 10))

        # Results TreeView
        tree_frame = tk.Frame(categories_section, bg=self.colors['bg_card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", style="Modern.Vertical.TScrollbar")
        self.tree = ttk.Treeview(tree_frame, columns=("count",), show="tree headings", style="Treeview", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree.yview)

        self.tree.heading("#0", text="Category")
        self.tree.heading("count", text="Count")
        self.tree.column("#0", width=150)
        self.tree.column("count", width=50, anchor="e")

        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- Right Panel ---
        # Top navigation bar
        nav_bar = tk.Frame(self.right_frame, bg=self.colors['bg_primary'], height=60)
        nav_bar.pack(fill=tk.X, pady=(0, 20))
        nav_bar.pack_propagate(False)

        # Zoom controls (left side)
        zoom_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        zoom_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.zoom_out_btn = tk.Button(zoom_frame,
                                     text="🔍-",
                                     command=self.zoom_out,
                                     font=("Segoe UI", 14),
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'],
                                     activebackground=self.colors['bg_card'],
                                     bd=0, relief=tk.FLAT, cursor="hand2",
                                     padx=12, pady=8)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.zoom_out_btn, "Decrease thumbnail size\nMake thumbnails smaller to see more images at once")

        self.zoom_in_btn = tk.Button(zoom_frame,
                                    text="🔍+",
                                    command=self.zoom_in,
                                    font=("Segoe UI", 14),
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_primary'],
                                    activebackground=self.colors['bg_card'],
                                    bd=0, relief=tk.FLAT, cursor="hand2",
                                    padx=12, pady=8)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.zoom_in_btn, "Increase thumbnail size\nMake thumbnails larger for better detail")

        self.zoom_label = tk.Label(zoom_frame,
                                  text="100%",
                                  font=("Segoe UI", 12),
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_secondary'])
        self.zoom_label.pack(side=tk.LEFT, fill=tk.Y)

        # Action buttons (right-aligned)
        action_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.select_all_btn_var = tk.StringVar(value="Select All")
        self.select_all_btn = ModernButton.create_primary_button(
            action_frame, "", self.select_all_photos, self.colors,
            textvariable=self.select_all_btn_var)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.select_all_btn, "Toggle selection for all visible photos")

        self.clean_btn_var = tk.StringVar(value="Clean (0)")
        self.clean_btn = ModernButton.create_danger_button(
            action_frame, "", self.clean_selected_photos, self.colors,
            textvariable=self.clean_btn_var)
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.clean_btn, "Move selected blurry photos to the trash")

        # Main thumbnail container
        thumb_container = tk.Frame(self.right_frame, bg=self.colors['bg_primary'])
        thumb_container.pack(fill=tk.BOTH, expand=True)

        # Pagination controls at top
        self.page_frame = tk.Frame(thumb_container, bg=self.colors['bg_primary'], height=50)
        self.page_frame.pack(fill=tk.X, pady=(0, 20))
        self.page_frame.pack_propagate(False)

        # Center container for navigation
        nav_center = tk.Frame(self.page_frame, bg=self.colors['bg_primary'])
        nav_center.pack(expand=True)

        nav_btn_style = {"font": ("Segoe UI", 12),
                        "bg": self.colors['bg_secondary'],
                        "fg": self.colors['text_primary'],
                        "activebackground": self.colors['bg_card'],
                        "activeforeground": self.colors['text_primary'],
                        "bd": 0, "padx": 20, "pady": 8, "cursor": "hand2"}

        self.prev_page_btn = tk.Button(nav_center, text="← Previous", command=self.prev_page, **nav_btn_style)
        self.prev_page_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.page_label = tk.Label(nav_center, text="Page 1 of 1",
                                  font=("Segoe UI", 12, "bold"),
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_primary'])
        self.page_label.pack(side=tk.LEFT, padx=20)

        self.next_page_btn = tk.Button(nav_center, text="Next →", command=self.next_page, **nav_btn_style)
        self.next_page_btn.pack(side=tk.LEFT, padx=(15, 0))

        self.page_frame.pack_forget()  # Hide initially

        # Thumbnail display area
        content_frame = tk.Frame(thumb_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.thumb_canvas = tk.Canvas(content_frame, bg=self.colors['bg_primary'], highlightthickness=0, bd=0)
        self.thumb_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.thumb_canvas.yview, style="Modern.Vertical.TScrollbar")
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg=self.colors['bg_primary'])

        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_canvas.create_window((0, 0), window=self.thumbs_frame, anchor="nw")
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))

        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind canvas configure event
        self.thumb_canvas.bind("<Configure>", self.on_canvas_configure)

        self.thumb_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Status bar
        self.status_bar = StatusBar(self.root, colors=self.colors)
        self.status_bar.set_text("Ready")

    def _on_mousewheel(self, event):
        if self.thumb_canvas.winfo_exists():
            self.thumb_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event=None):
        """Handle canvas resize events and refresh layout if needed"""
        # Update scroll region
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))

        # Only refresh layout if width changed significantly
        if event and hasattr(self, 'last_width') and abs(event.width - self.last_width) < 50:
            return

        self.last_width = event.width if event else self.thumb_canvas.winfo_width()

        # If we have current paths displayed, refresh the layout
        if hasattr(self, 'current_paths') and self.current_paths:
            self.show_thumbnails_for_category(self.tree.selection()[0] if self.tree.selection() else "blurry")

    def zoom_in(self):
        """Increase thumbnail size"""
        width, height = self.thumb_size
        new_width = min(width + 60, self.max_thumb_size[0])
        new_height = min(height + 45, self.max_thumb_size[1])

        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.image_cache.clear()  # Clear cache to force regeneration at new size
            self.update_zoom_controls()
            if self.current_paths:
                self.display_page()

    def zoom_out(self):
        """Decrease thumbnail size"""
        width, height = self.thumb_size
        new_width = max(width - 60, self.min_thumb_size[0])
        new_height = max(height - 45, self.min_thumb_size[1])

        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.image_cache.clear()  # Clear cache to force regeneration at new size
            self.update_zoom_controls()
            if self.current_paths:
                self.display_page()

    def update_zoom_controls(self):
        """Update zoom button states and percentage label"""
        can_zoom_in = self.thumb_size[0] < self.max_thumb_size[0]
        can_zoom_out = self.thumb_size[0] > self.min_thumb_size[0]

        self.zoom_in_btn.config(state=tk.NORMAL if can_zoom_in else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if can_zoom_out else tk.DISABLED)

        # Calculate zoom percentage (based on width)
        zoom_percent = int((self.thumb_size[0] / 240) * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")

    def _get_image_count(self, folder_path):
        """Quickly count the number of images in a folder, excluding Trash."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        count = 0
        try:
            for ext in image_extensions:
                # Get all matching files and exclude Trash folder
                for img_path in Path(folder_path).rglob(f'*{ext}'):
                    if 'Trash' not in img_path.parts:
                        count += 1
                for img_path in Path(folder_path).rglob(f'*{ext.upper()}'):
                    if 'Trash' not in img_path.parts:
                        count += 1
            return count
        except Exception as e:
            print(f"Error counting images: {e}")
            return 0

    def update_threshold_label(self, value):
        self.lbl_threshold.config(text=f"Current: {float(value):.1f}")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.lbl_folder.config(text=folder)
            self.status_bar.set_text(f"Selected folder: {folder}")
            # Update trash count when folder is selected
            self.trash_manager.update_trash_count()

    def start_scan(self):
        if not self.folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        total_images = self._get_image_count(self.folder)
        if total_images == 0:
            messagebox.showinfo("No Images Found", "No supported image files were found in the selected folder.")
            return

        self.progress_window.show(total=total_images, initial_text="Preparing to scan...")
        threshold = self.threshold_var.get()

        threading.Thread(target=self._scan_thread, args=(self.folder, threshold), daemon=True).start()

    def _scan_thread(self, folder, threshold):
        def progress_callback(current, total, filename):
            # Ensure updates happen on the main thread
            self.root.after(0, self.progress_window.update, current, total, f"Processing: {filename}", f"{current}/{total}")

        # Use batch processing for better performance
        results = detect_blurry_images_batch(folder, threshold, progress_callback)
        self.root.after(0, self.on_scan_complete, results)

    def on_scan_complete(self, results):
        self.progress_window.close()
        self.blurry_images = results['blurry_images']
        self.sharp_images = results['sharp_images']

        # Cache blur scores for fast lookup during display
        self.blur_scores.clear()
        for path, score in self.blurry_images:
            self.blur_scores[path] = score
        for path, score in self.sharp_images:
            self.blur_scores[path] = score

        # Clear previous tree entries
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Populate tree
        self.tree.insert("", "end", "blurry", text="Blurry Images", values=(len(self.blurry_images),))
        self.tree.insert("", "end", "sharp", text="Sharp Images", values=(len(self.sharp_images),))

        self.status_bar.set_text(f"Scan complete. Found {len(self.blurry_images)} blurry images.")

        # Automatically select and show blurry images
        if self.blurry_images:
            self.tree.selection_set("blurry")
            self.show_thumbnails_for_category("blurry")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        category = selected_item[0]
        self.show_thumbnails_for_category(category)

    def show_thumbnails_for_category(self, category):
        if category == "blurry":
            self.current_paths = [p for p, s in self.blurry_images]
        elif category == "sharp":
            self.current_paths = [p for p, s in self.sharp_images]
        else:
            self.current_paths = []

        self.current_page = 0
        self.display_page()

        # Show pagination if we have images
        if self.current_paths:
            self.page_frame.pack(fill=tk.X, pady=(0, 20))
        else:
            self.page_frame.pack_forget()

    def display_page(self):
        self.root.config(cursor="wait")

        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.selected_check_vars.clear()

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_paths = self.current_paths[start_idx:end_idx]

        # Calculate grid layout based on thumbnail size
        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width < 200: canvas_width = 1000  # Default width
        thumb_width = self.thumb_size[0] + 30  # Add padding
        cols = max(1, canvas_width // thumb_width)

        for idx, path in enumerate(page_paths):
            row, col = divmod(idx, cols)

            # Configure grid weights
            self.thumbs_frame.grid_columnconfigure(col, weight=1)

            # Modern card with rounded corners
            card = tk.Frame(self.thumbs_frame, bd=0,
                           bg=self.colors['bg_card'],
                           highlightbackground=self.colors['bg_secondary'],
                           highlightthickness=1,
                           relief=tk.SOLID)
            card.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            # Image container with padding
            img_container = tk.Frame(card, bg=self.colors['bg_card'])
            img_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

            img_tk = self.get_thumbnail(path)
            self.thumb_imgs.append(img_tk)

            # Canvas for image with overlay support
            img_canvas = tk.Canvas(img_container,
                                 width=img_tk.width(),
                                 height=img_tk.height(),
                                 bg=self.colors['bg_card'],
                                 highlightthickness=0, bd=0)
            img_canvas.pack()

            # Draw image on canvas
            img_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            img_canvas.image = img_tk  # Keep reference

            # Store canvas reference for overlay updates
            setattr(img_canvas, 'img_path', path)

            # Add double-click to open full image
            img_canvas.bind('<Double-Button-1>', lambda e, p=path: self.open_full_image(p))

            # Modern hover effects
            def on_enter(ev, c=card):
                c.config(highlightbackground=self.colors['accent'], highlightthickness=2)
            def on_leave(ev, c=card):
                c.config(highlightbackground=self.colors['bg_secondary'], highlightthickness=1)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            img_canvas.bind("<Enter>", on_enter)
            img_canvas.bind("<Leave>", on_leave)

            # Info section at bottom
            info_frame = tk.Frame(card, bg=self.colors['bg_card'])
            info_frame.pack(fill=tk.X, padx=1, pady=1)

            var = tk.BooleanVar()
            filename = os.path.basename(path)
            if len(filename) > 25:
                filename = filename[:22] + "..."

            chk = tk.Checkbutton(info_frame,
                               text=filename,
                               variable=var,
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['bg_card'],
                               fg=self.colors['text_primary'],
                               activebackground=self.colors['bg_card'],
                               selectcolor=self.colors['accent'],
                               bd=0, highlightthickness=0,
                               anchor="w", padx=1, pady=1)
            chk.pack(fill=tk.X, padx=1, pady=1)

            var.trace_add('write', lambda *args, v=var, p=path, c=img_canvas: self.on_image_check(v, p, c))
            self.selected_check_vars.append((var, path, img_canvas))

            # Get blur score from cache (already calculated during scan)
            score = self.blur_scores.get(path, 0)
            quality = self.detector.get_blur_quality(score)

            # Color code based on quality
            if quality in ["Excellent", "Good"]:
                score_color = self.colors['success']
            elif quality == "Fair":
                score_color = self.colors['accent']
            elif quality == "Poor":
                score_color = self.colors['warning']
            else:
                score_color = self.colors['danger']

            score_label = tk.Label(info_frame,
                                   text=f"Score: {score:.2f} ({quality})",
                                   bg=self.colors['bg_card'],
                                   fg=score_color,
                                   font=("Segoe UI", 9),
                                   anchor="w", padx=1, pady=1)
            score_label.pack(fill=tk.X, padx=1, pady= 1)

            # Add tooltip with blur score explanation
            tooltip_text = self.get_blur_score_tooltip(score, quality)
            ToolTip(score_label, tooltip_text)

        self.update_page_controls()
        self.update_zoom_controls()
        self.root.config(cursor="")
        self.thumb_canvas.yview_moveto(0)

    def get_thumbnail(self, path):
        cache_key = (path, self.thumb_size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        try:
            img = Image.open(path)
            img.thumbnail(self.thumb_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = img_tk
            return img_tk
        except Exception as e:
            print(f"Error creating thumbnail for {path}: {e}")
            return None

    def calculate_columns(self):
        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width < 200: canvas_width = self.right_frame.winfo_width()
        thumb_width = self.thumb_size[0] + 30 # thumb size + padding
        return max(1, canvas_width // thumb_width)

    def get_blur_score_tooltip(self, score, quality):
        """Generate helpful tooltip text for blur scores"""
        if quality == "Excellent":
            explanation = "This image is very sharp with excellent detail."
        elif quality == "Good":
            explanation = "This image is sharp with good detail."
        elif quality == "Fair":
            explanation = "This image has acceptable sharpness but may lack some detail."
        elif quality == "Poor":
            explanation = "This image shows noticeable blur and lacks fine detail."
        else:  # Very Blurry
            explanation = "This image is significantly blurred or out of focus."

        tooltip = f"Blur Score: {score:.2f}\n"
        tooltip += f"Quality: {quality}\n\n"
        tooltip += explanation

        tooltip += f"\n\nHow it works:\n"
        tooltip += f"Higher scores (>100) indicate sharper images.\n"
        tooltip += f"Lower scores (<100) indicate blurrier images.\n"
        tooltip += f"The score measures edge sharpness using the Laplacian operator."

        if score < 100:
            tooltip += "\n\nTip: Consider reviewing or removing blurry images to maintain photo quality."

        return tooltip

    def update_page_controls(self):
        total_pages = max(1, (len(self.current_paths) - 1) // self.page_size + 1) if self.current_paths else 1
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if (self.current_page + 1) < total_pages else tk.DISABLED)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def next_page(self):
        total_pages = (len(self.current_paths) - 1) // self.page_size + 1
        if (self.current_page + 1) < total_pages:
            self.current_page += 1
            self.display_page()

    def select_all_photos(self):
        if not self.selected_check_vars: return

        # Determine new state based on the first checkbox
        current_state = self.selected_check_vars[0][0].get()
        new_state = not current_state

        for var, path, canvas in self.selected_check_vars:
            var.set(new_state)
            ImageUtils.update_cross_overlay(self.selected_check_vars, var, path, self._trash_icon_cache)

        self.update_select_all_button_text()

    def update_select_all_button_text(self):
        if not self.selected_check_vars:
            self.select_all_btn_var.set("Select All")
            return

        all_selected = all(var.get() for var, _, _ in self.selected_check_vars)
        self.select_all_btn_var.set("Unselect All" if all_selected else "Select All")

    def count_selected_photos(self):
        return sum(1 for var, _, _ in self.selected_check_vars if var.get())

    def on_image_check(self, var, path, canvas):
        """Handle checkbox state changes and update trash overlay"""
        ImageUtils.update_cross_overlay(self.selected_check_vars, var, path, self._trash_icon_cache)
        count = self.count_selected_photos()
        self.clean_btn_var.set(f"Clean ({count})")
        self.update_select_all_button_text()

    def clean_selected_photos(self):
        # Prevent concurrent cleaning operations
        if self._cleaning_in_progress:
            return

        selected_paths = [path for var, path, _ in self.selected_check_vars if var.get()]
        if not selected_paths:
            messagebox.showinfo("Clean", "No photos selected.")
            return

        if not self.folder:
            messagebox.showerror("Error", "No folder selected.")
            return

        # Set cleaning flag
        self._cleaning_in_progress = True

        try:
            # Move files to trash using shared functionality
            moved_count, failed_files = FileOperations.move_images_to_trash(selected_paths, self.folder)

            # Show completion popup using shared functionality
            FileOperations.show_clean_completion_popup(self.root, moved_count, failed_files)

            # Update trash count
            self.trash_manager.update_trash_count()

            # Refresh UI - remove moved photos from the lists
            self.on_scan_complete({
                'blurry_images': [(p, s) for p, s in self.blurry_images if p not in selected_paths],
                'sharp_images': [(p, s) for p, s in self.sharp_images if p not in selected_paths],
            })

        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean selected photos: {str(e)}")
        finally:
            # Reset cleaning flag
            self._cleaning_in_progress = False

    def open_full_image(self, path):
        ImageUtils.open_full_image(self.root, path)

if __name__ == '__main__':
    root = tk.Tk()
    app = BlurryImageDetectionApp(root)
    root.mainloop()
