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
from BlurryImageDetection import detect_blurry_images, get_recommended_threshold, BlurryImageDetector
from CommonUI import (ToolTip, ModernColors, ProgressWindow, ModernStyling, 
                     StatusBar, ZoomControls, ModernButton, ImageUtils, TrashManager)

class BlurryImageDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Blurry Image Detector")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)

        self.folder = ""
        self.blurry_images = []
        self.sharp_images = []
        self.current_paths = []
        self.current_page = 0
        self.page_size = 20
        self.thumb_imgs = []
        self.image_cache = {}
        self.selected_check_vars = []
        self._cleaning_in_progress = False
        self.detector = BlurryImageDetector()

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

        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel for controls and results
        left_panel = tk.Frame(main_frame, width=300, bg=self.colors['bg_secondary'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        # Right panel for thumbnails
        self.right_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Left Panel ---
        # Folder selection
        folder_frame = tk.Frame(left_panel, bg=self.colors['bg_secondary'])
        folder_frame.pack(fill=tk.X, padx=15, pady=15)
        
        btn_select = ModernButton.create_primary_button(folder_frame, text="Select Folder", command=self.select_folder, colors=self.colors)
        btn_select.pack(fill=tk.X)
        ToolTip(btn_select, "Select a folder to scan for blurry images")

        self.lbl_folder = tk.Label(folder_frame, text="No folder selected", 
                                   wraplength=270, justify=tk.LEFT,
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                   font=("Segoe UI", 9))
        self.lbl_folder.pack(pady=(10, 0))

        # Threshold control
        threshold_frame = tk.Frame(left_panel, bg=self.colors['bg_secondary'])
        threshold_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(threshold_frame, text="Blur Threshold", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor="w")

        self.threshold_var = tk.DoubleVar(value=100.0)
        self.threshold_slider = ttk.Scale(threshold_frame, from_=10, to=300, 
                                          orient=tk.HORIZONTAL, variable=self.threshold_var,
                                          command=self.update_threshold_label)
        self.threshold_slider.pack(fill=tk.X, pady=(5, 0))
        ToolTip(self.threshold_slider, "Adjust the sensitivity for blur detection.\nLower values detect only very blurry images.")

        self.lbl_threshold = tk.Label(threshold_frame, text="Current: 100.0",
                                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                      font=("Segoe UI", 9))
        self.lbl_threshold.pack(anchor="w")

        # Scan button
        btn_scan = ModernButton.create_primary_button(left_panel, text="Start Scan", command=self.start_scan, colors=self.colors)
        btn_scan.pack(fill=tk.X, padx=15)
        ToolTip(btn_scan, "Begin scanning the selected folder for blurry images")

        # Results TreeView
        tree_frame = tk.Frame(left_panel, bg=self.colors['bg_secondary'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

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
        nav_bar = tk.Frame(self.right_frame, bg=self.colors['bg_primary'], height=50)
        nav_bar.pack(fill=tk.X, pady=(0, 10))
        nav_bar.pack_propagate(False)

        # Action buttons (right-aligned)
        action_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))

        self.select_all_btn_var = tk.StringVar(value="Select All")
        self.select_all_btn = ModernButton.create_secondary_button(action_frame, "", command=self.select_all_photos, colors=self.colors, textvariable=self.select_all_btn_var)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.select_all_btn, "Toggle selection for all visible photos")

        self.clean_btn_var = tk.StringVar(value="Clean (0)")
        self.clean_btn = ModernButton.create_danger_button(action_frame, "", command=self.clean_selected_photos, colors=self.colors, textvariable=self.clean_btn_var)
        self.clean_btn.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.clean_btn, "Move selected blurry photos to the trash")

        self.trash_manager = TrashManager(
            parent_frame=action_frame,
            colors=self.colors,
            folder_callback=lambda: self.folder,
            img_extensions={'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'},
            button_style="text"
        )
        self.trash_manager.pack(side=tk.LEFT)

        # Pagination controls (centered)
        self.page_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        self.page_frame.pack(expand=True)

        self.prev_page_btn = ModernButton.create_secondary_button(self.page_frame, text="<< Prev", command=self.prev_page, colors=self.colors)
        self.prev_page_btn.pack(side=tk.LEFT)
        
        self.page_label = tk.Label(self.page_frame, text="Page 1/1", bg=self.colors['bg_primary'], fg=self.colors['text_primary'], font=("Segoe UI", 11))
        self.page_label.pack(side=tk.LEFT, padx=15)
        
        self.next_page_btn = ModernButton.create_secondary_button(self.page_frame, text="Next >>", command=self.next_page, colors=self.colors)
        self.next_page_btn.pack(side=tk.LEFT)

        # Thumbnail display area
        self.thumb_canvas = tk.Canvas(self.right_frame, bg=self.colors['bg_primary'], highlightthickness=0)
        self.thumb_scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.thumb_canvas.yview, style="Modern.Vertical.TScrollbar")
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg=self.colors['bg_primary'])

        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_canvas.create_window((0, 0), window=self.thumbs_frame, anchor="nw")
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))

        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thumb_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Status bar
        self.status_bar = StatusBar(self.root, colors=self.colors)
        self.status_bar.set_text("Ready")

    def _on_mousewheel(self, event):
        if self.thumb_canvas.winfo_exists():
            self.thumb_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _get_image_count(self, folder_path):
        """Quickly count the number of images in a folder."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        count = 0
        try:
            for ext in image_extensions:
                count += len(list(Path(folder_path).rglob(f'*{ext}')))
                count += len(list(Path(folder_path).rglob(f'*{ext.upper()}')))
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

        results = detect_blurry_images(folder, threshold, progress_callback)
        self.root.after(0, self.on_scan_complete, results)

    def on_scan_complete(self, results):
        self.progress_window.close()
        self.blurry_images = results['blurry_images']
        self.sharp_images = results['sharp_images']

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

    def display_page(self):
        self.root.config(cursor="wait")
        
        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.selected_check_vars.clear()

        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_paths = self.current_paths[start_idx:end_idx]

        cols = self.calculate_columns()
        
        for idx, path in enumerate(page_paths):
            row, col = divmod(idx, cols)
            
            card = tk.Frame(self.thumbs_frame, bd=1, relief=tk.SOLID, bg=self.colors['bg_card'],
                            highlightbackground=self.colors['bg_secondary'], highlightthickness=1)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            img_tk = self.get_thumbnail(path)
            self.thumb_imgs.append(img_tk)

            lbl_img = tk.Label(card, image=img_tk, bg=self.colors['bg_card'])
            lbl_img.pack(pady=5)
            lbl_img.bind('<Double-Button-1>', lambda e, p=path: self.open_full_image(p))

            var = tk.BooleanVar()
            chk = tk.Checkbutton(card, text=os.path.basename(path), variable=var,
                                 bg=self.colors['bg_card'], fg=self.colors['text_primary'],
                                 selectcolor=self.colors['bg_secondary'], activebackground=self.colors['bg_card'],
                                 font=("Segoe UI", 8))
            chk.pack(anchor="w", padx=5)
            var.trace_add('write', lambda *args: self.update_clean_btn_label())
            self.selected_check_vars.append((var, path))

            score = self.detector.calculate_blur_score(path)
            quality = self.detector.get_blur_quality(score)
            score_label = tk.Label(card, text=f"Score: {score:.2f} ({quality})", 
                                   bg=self.colors['bg_card'], fg=self.colors['text_secondary'],
                                   font=("Segoe UI", 8))
            score_label.pack(anchor="w", padx=5, pady=(0,5))

        self.update_page_controls()
        self.update_clean_btn_label()
        self.root.config(cursor="")
        self.thumb_canvas.yview_moveto(0)

    def get_thumbnail(self, path):
        thumb_size = (150, 150)
        if (path, thumb_size) in self.image_cache:
            return self.image_cache[(path, thumb_size)]
        
        try:
            img = Image.open(path)
            img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[(path, thumb_size)] = img_tk
            return img_tk
        except Exception as e:
            print(f"Error creating thumbnail for {path}: {e}")
            return None

    def calculate_columns(self):
        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width < 200: canvas_width = self.right_frame.winfo_width()
        thumb_width = 150 + 20 # thumb size + padding
        return max(1, canvas_width // thumb_width)

    def update_page_controls(self):
        total_pages = (len(self.current_paths) - 1) // self.page_size + 1
        self.page_label.config(text=f"Page {self.current_page + 1}/{total_pages}")
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
        
        for var, _ in self.selected_check_vars:
            var.set(new_state)
        
        self.update_select_all_button_text()

    def update_select_all_button_text(self):
        if not self.selected_check_vars:
            self.select_all_btn_var.set("Select All")
            return
        
        all_selected = all(var.get() for var, _ in self.selected_check_vars)
        self.select_all_btn_var.set("Unselect All" if all_selected else "Select All")

    def count_selected_photos(self):
        return sum(1 for var, _ in self.selected_check_vars if var.get())

    def update_clean_btn_label(self):
        count = self.count_selected_photos()
        self.clean_btn_var.set(f"Clean ({count})")
        self.update_select_all_button_text()

    def clean_selected_photos(self):
        selected_paths = [path for var, path in self.selected_check_vars if var.get()]
        if not selected_paths:
            messagebox.showinfo("Clean", "No photos selected to clean.")
            return

        if not self.folder:
            messagebox.showerror("Error", "Base folder not set.")
            return

        confirm = messagebox.askyesno("Confirm Clean", 
            f"Are you sure you want to move {len(selected_paths)} photos to the trash?")
        if not confirm:
            return

        self._cleaning_in_progress = True
        self.status_bar.set_text("Cleaning selected photos...")
        
        moved_count = 0
        try:
            for path in selected_paths:
                self.trash_manager.move_to_trash(path, self.folder)
                moved_count += 1
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during cleaning: {e}")
        
        self.status_bar.set_text(f"Successfully moved {moved_count} photos to trash.")
        self._cleaning_in_progress = False
        
        # Refresh the view
        self.on_scan_complete({
            'blurry_images': [(p, s) for p, s in self.blurry_images if p not in selected_paths],
            'sharp_images': [(p, s) for p, s in self.sharp_images if p not in selected_paths],
        })

    def open_full_image(self, path):
        ImageUtils.open_full_image(self.root, path)

if __name__ == '__main__':
    root = tk.Tk()
    app = BlurryImageDetectionApp(root)
    root.mainloop()
