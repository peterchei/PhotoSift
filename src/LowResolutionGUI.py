"""
GUI for Low Resolution Image Detection
Provides a user interface to detect low-resolution images in a folder and manage them.
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
from LowResolutionDetection import detect_low_res_images_batch, get_recommended_thresholds, LowResolutionDetector
from CommonUI import (ToolTip, ModernColors, ProgressWindow, ModernStyling,
                     StatusBar, ZoomControls, ModernButton, ImageUtils, TrashManager, FileOperations)

class LowResolutionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoSift - Low Resolution Detector")
        # Maximize window on startup
        self.root.state('zoomed')  # Windows maximized state

        self.folder = ""
        self.low_res_images = []   # list of (path, width, height)
        self.ok_images = []        # list of (path, width, height)
        self.dimensions = {}       # path -> (width, height)
        self.current_paths = []
        self.current_page = 0
        self.page_size = 50
        self.thumb_imgs = []
        self.image_cache = {}
        self.selected_check_vars = []
        self._trash_icon_cache = {}
        self._cleaning_in_progress = False
        self.detector = LowResolutionDetector()

        # Thumbnail size configuration
        self.thumb_size = (240, 180)
        self.min_thumb_size = (60, 45)
        self.max_thumb_size = (580, 360)

        # Use centralized color scheme
        self.colors = ModernColors.get_color_scheme()

        # Initialize progress window
        self.progress_window = ProgressWindow(self.root, "Low Resolution Detection")

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
                                 text="Low Resolution Detector",
                                 font=("Segoe UI", 14),
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor="w")

        # Header buttons frame
        header_buttons = tk.Frame(header, bg=self.colors['bg_primary'])
        header_buttons.pack(side=tk.RIGHT, fill=tk.Y)

        # Create trash manager
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
        ToolTip(btn_select, "Select a folder to scan for low resolution photos")

        self.lbl_folder = tk.Label(folder_frame, text="No folder selected",
                                   wraplength=260, justify=tk.LEFT,
                                   bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                                   font=("Segoe UI", 10))
        self.lbl_folder.pack(fill=tk.X, pady=(8, 0))

        # Threshold control — width × height spinboxes + presets
        threshold_frame = tk.Frame(left_panel, bg=self.colors['bg_sidebar'])
        threshold_frame.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(threshold_frame, text="Minimum Resolution",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors['bg_sidebar'], fg=self.colors['text_primary']).pack(anchor="w")

        # Width × Height spinboxes
        dim_row = tk.Frame(threshold_frame, bg=self.colors['bg_sidebar'])
        dim_row.pack(fill=tk.X, pady=(8, 4))

        tk.Label(dim_row, text="W:", bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.min_width_var = tk.IntVar(value=1280)
        tk.Spinbox(dim_row, from_=1, to=9999, textvariable=self.min_width_var, width=6,
                   font=("Segoe UI", 10), bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                   buttonbackground=self.colors['bg_secondary'], relief=tk.FLAT).pack(side=tk.LEFT, padx=(2, 8))

        tk.Label(dim_row, text="H:", bg=self.colors['bg_sidebar'], fg=self.colors['text_secondary'],
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.min_height_var = tk.IntVar(value=720)
        tk.Spinbox(dim_row, from_=1, to=9999, textvariable=self.min_height_var, width=6,
                   font=("Segoe UI", 10), bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                   buttonbackground=self.colors['bg_secondary'], relief=tk.FLAT).pack(side=tk.LEFT, padx=(2, 0))

        # Preset buttons
        preset_row = tk.Frame(threshold_frame, bg=self.colors['bg_sidebar'])
        preset_row.pack(fill=tk.X, pady=(4, 0))

        presets = [
            ("480p",  640,  480),
            ("720p",  1280, 720),
            ("1080p", 1920, 1080),
        ]
        for label, w, h in presets:
            btn = tk.Button(preset_row, text=label, font=("Segoe UI", 9),
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            activebackground=self.colors['accent'], activeforeground=self.colors['text_primary'],
                            bd=0, relief=tk.FLAT, cursor="hand2", padx=8, pady=3,
                            command=lambda _w=w, _h=h: self._apply_preset(_w, _h))
            btn.pack(side=tk.LEFT, padx=(0, 4))
            ToolTip(btn, f"Flag images below {w}x{h}")

        # Scan button
        btn_scan = ModernButton.create_primary_button(left_panel, text="Start Scan", command=self.start_scan, colors=self.colors)
        btn_scan.pack(fill=tk.X, padx=20)
        ToolTip(btn_scan, "Begin scanning the selected folder for low resolution images")

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

        self.clean_btn_var = tk.StringVar(value="Clean (0)")
        self.clean_btn = ModernButton.create_danger_button(
            action_frame, "", self.clean_selected_photos, self.colors,
            textvariable=self.clean_btn_var)
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 10))

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
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
        if event and hasattr(self, 'last_width') and abs(event.width - self.last_width) < 50:
            return
        self.last_width = event.width if event else self.thumb_canvas.winfo_width()
        if hasattr(self, 'current_paths') and self.current_paths:
            sel = self.tree.selection()
            self.show_thumbnails_for_category(sel[0] if sel else "low_res")

    def _apply_preset(self, width, height):
        self.min_width_var.set(width)
        self.min_height_var.set(height)

    def zoom_in(self):
        width, height = self.thumb_size
        new_width = min(width + 60, self.max_thumb_size[0])
        new_height = min(height + 45, self.max_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.image_cache.clear()
            self.update_zoom_controls()
            if self.current_paths:
                self.display_page()

    def zoom_out(self):
        width, height = self.thumb_size
        new_width = max(width - 60, self.min_thumb_size[0])
        new_height = max(height - 45, self.min_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.image_cache.clear()
            self.update_zoom_controls()
            if self.current_paths:
                self.display_page()

    def update_zoom_controls(self):
        can_zoom_in = self.thumb_size[0] < self.max_thumb_size[0]
        can_zoom_out = self.thumb_size[0] > self.min_thumb_size[0]
        self.zoom_in_btn.config(state=tk.NORMAL if can_zoom_in else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if can_zoom_out else tk.DISABLED)
        zoom_percent = int((self.thumb_size[0] / 240) * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")

    def _get_image_count(self, folder_path):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        count = 0
        try:
            for ext in image_extensions:
                for img_path in Path(folder_path).rglob(f'*{ext}'):
                    if 'Trash' not in img_path.parts: count += 1
                for img_path in Path(folder_path).rglob(f'*{ext.upper()}'):
                    if 'Trash' not in img_path.parts: count += 1
            return count
        except Exception as e:
            print(f"Error counting images: {e}")
            return 0

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.lbl_folder.config(text=folder)
            self.status_bar.set_text(f"Selected folder: {folder}")
            self.trash_manager.update_trash_count()

    def start_scan(self):
        if not self.folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        total_images = self._get_image_count(self.folder)
        if total_images == 0:
            messagebox.showinfo("No Images Found", "No images found in the selected folder.")
            return
        self.progress_window.show(total=total_images, initial_text="Preparing to scan...")
        min_width = self.min_width_var.get()
        min_height = self.min_height_var.get()
        threading.Thread(target=self._scan_thread, args=(self.folder, min_width, min_height), daemon=True).start()

    def _scan_thread(self, folder, min_width, min_height):
        def progress_callback(current, total, filename):
            self.root.after(0, self.progress_window.update, current, total, f"Processing: {filename}", f"{current}/{total}")
        results = detect_low_res_images_batch(folder, min_width=min_width, min_height=min_height,
                                               progress_callback=progress_callback)
        self.root.after(0, self.on_scan_complete, results)

    def on_scan_complete(self, results):
        self.progress_window.close()
        self.low_res_images = results['low_res_images']
        self.ok_images = results['ok_images']
        self.dimensions.clear()
        for path, w, h in self.low_res_images: self.dimensions[path] = (w, h)
        for path, w, h in self.ok_images: self.dimensions[path] = (w, h)

        for i in self.tree.get_children(): self.tree.delete(i)
        self.tree.insert("", "end", "low_res", text="Low Resolution", values=(len(self.low_res_images),))
        self.tree.insert("", "end", "ok", text="OK Resolution", values=(len(self.ok_images),))

        self.status_bar.set_text(f"Scan complete. Found {len(self.low_res_images)} low resolution images.")
        if self.low_res_images:
            self.tree.selection_set("low_res")
            self.show_thumbnails_for_category("low_res")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item: return
        category = selected_item[0]
        self.show_thumbnails_for_category(category)

    def show_thumbnails_for_category(self, category):
        if category == "low_res":
            self.current_paths = [p for p, w, h in self.low_res_images]
        elif category == "ok":
            self.current_paths = [p for p, w, h in self.ok_images]
        else:
            self.current_paths = []
        self.current_page = 0
        self.display_page()
        if self.current_paths:
            self.page_frame.pack(fill=tk.X, pady=(0, 20))
        else:
            self.page_frame.pack_forget()

    def display_page(self):
        self.root.config(cursor="wait")
        for widget in self.thumbs_frame.winfo_children(): widget.destroy()
        self.thumb_imgs.clear()
        self.selected_check_vars.clear()

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_paths = self.current_paths[start_idx:end_idx]

        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width < 200: canvas_width = 1000
        thumb_width = self.thumb_size[0] + 30
        cols = max(1, canvas_width // thumb_width)

        for idx, path in enumerate(page_paths):
            row, col = divmod(idx, cols)
            self.thumbs_frame.grid_columnconfigure(col, weight=1)
            card = tk.Frame(self.thumbs_frame, bd=0, bg=self.colors['bg_card'], highlightthickness=1, relief=tk.SOLID)
            card.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            img_tk = self.get_thumbnail(path)
            self.thumb_imgs.append(img_tk)
            if img_tk is not None:
                img_canvas = tk.Canvas(card, width=img_tk.width(), height=img_tk.height(), bg=self.colors['bg_card'], highlightthickness=0, bd=0)
                img_canvas.pack(pady=5)
                img_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                img_canvas.image = img_tk  # Keep reference to prevent GC blanking
                img_canvas.bind('<Double-Button-1>', lambda e, p=path: self.open_full_image(p))
            else:
                img_canvas = tk.Canvas(card, width=self.thumb_size[0], height=self.thumb_size[1], bg=self.colors['bg_card'], highlightthickness=0, bd=0)
                img_canvas.pack(pady=5)
                img_canvas.create_text(self.thumb_size[0]//2, self.thumb_size[1]//2, text="No Preview", fill=self.colors.get('text_secondary', 'gray'))
                img_canvas.bind('<Double-Button-1>', lambda e, p=path: self.open_full_image(p))

            info_frame = tk.Frame(card, bg=self.colors['bg_card'])
            info_frame.pack(fill=tk.X, padx=5, pady=5)

            var = tk.BooleanVar()
            filename = os.path.basename(path)
            if len(filename) > 25: filename = filename[:22] + "..."
            chk = tk.Checkbutton(info_frame, text=filename, variable=var, font=("Segoe UI", 10, "bold"), bg=self.colors['bg_card'], fg=self.colors['text_primary'], selectcolor=self.colors['accent'], bd=0)
            chk.pack(fill=tk.X)
            var.trace_add('write', lambda *args, v=var, p=path, c=img_canvas: self.on_image_check(v, p, c))
            self.selected_check_vars.append((var, path, img_canvas))

            dims = self.dimensions.get(path, (-1, -1))
            w, h = dims
            quality = self.detector.get_resolution_quality(w, h)
            is_low = any(p == path for p, _, _ in self.low_res_images)
            score_color = self.colors['danger'] if is_low else self.colors['success']
            dim_text = f"{w} x {h} ({quality})" if w != -1 else "Unknown"
            score_label = tk.Label(info_frame, text=dim_text, bg=self.colors['bg_card'], fg=score_color, font=("Segoe UI", 9))
            score_label.pack(fill=tk.X)
            ToolTip(score_label, f"Image dimensions: {w}x{h} pixels\nQuality: {quality}")

        self.update_page_controls()
        self.update_zoom_controls()
        self.root.config(cursor="")

    def get_thumbnail(self, path):
        cache_key = (path, self.thumb_size)
        if cache_key in self.image_cache: return self.image_cache[cache_key]
        try:
            img = Image.open(path)
            img.thumbnail(self.thumb_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = img_tk
            return img_tk
        except Exception: return None

    def update_page_controls(self):
        total_pages = max(1, (len(self.current_paths) - 1) // self.page_size + 1)
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if (self.current_page + 1) < total_pages else tk.DISABLED)

    def prev_page(self):
        if self.current_page > 0: self.current_page -= 1; self.display_page()

    def next_page(self):
        total_pages = (len(self.current_paths) - 1) // self.page_size + 1
        if (self.current_page + 1) < total_pages: self.current_page += 1; self.display_page()

    def select_all_photos(self):
        if not self.selected_check_vars: return
        new_state = not self.selected_check_vars[0][0].get()
        for var, path, canvas in self.selected_check_vars:
            var.set(new_state)
        self.update_select_all_button_text()

    def update_select_all_button_text(self):
        self.select_all_btn_var.set("Unselect All" if all(var.get() for var, _, _ in self.selected_check_vars) else "Select All")

    def on_image_check(self, var, path, canvas):
        ImageUtils.update_cross_overlay(self.selected_check_vars, var, path, self._trash_icon_cache)
        self.clean_btn_var.set(f"Clean ({sum(1 for v, _, _ in self.selected_check_vars if v.get())})")
        self.update_select_all_button_text()

    def clean_selected_photos(self):
        if self._cleaning_in_progress: return
        selected_paths = [path for var, path, _ in self.selected_check_vars if var.get()]
        if not selected_paths: messagebox.showinfo("Clean", "No photos selected."); return
        self._cleaning_in_progress = True
        try:
            moved_count, failed_files = FileOperations.move_images_to_trash(selected_paths, self.folder)
            FileOperations.show_clean_completion_popup(self.root, moved_count, failed_files)
            self.trash_manager.update_trash_count()
            self.on_scan_complete({
                'low_res_images': [(p, w, h) for p, w, h in self.low_res_images if p not in selected_paths],
                'ok_images': [(p, w, h) for p, w, h in self.ok_images if p not in selected_paths],
                'total_processed': 0,
                'total_low_res': 0,
            })
        except Exception as e: messagebox.showerror("Error", str(e))
        finally: self._cleaning_in_progress = False

    def open_full_image(self, path):
        ImageUtils.open_full_image(self.root, path)

if __name__ == '__main__':
    root = tk.Tk()
    app = LowResolutionApp(root)
    root.mainloop()
