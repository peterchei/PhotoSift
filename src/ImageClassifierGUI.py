
# Standard library imports
import os
import threading
import shutil

# Third-party imports
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Local imports
from ImageClassification import classify_people_vs_screenshot, IMG_EXT
from ImageClassification import classify_people_vs_screenshot_batch

class ImageClassifierApp:
    def select_all_photos(self):
        if not hasattr(self, 'selected_check_vars') or not self.selected_check_vars:
            return
            
        # Get current state from first checkbox to determine action
        first_var = self.selected_check_vars[0][0]
        new_state = not first_var.get()
        
        # Update all checkboxes
        for var, _ in self.selected_check_vars:
            var.set(new_state)
            
        # Update clean button label
        self.update_clean_btn_label(self.count_selected_photos())

    def show_selected_thumbnails(self, paths, force_page=False):
        # Use wait cursor during update
        self.root.config(cursor="wait")
        self.thumbs_frame.config(cursor="watch")
        
        # Clear previous thumbnails quickly
        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.img_panel.pack_forget()
        self.lbl_result.pack_forget()
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_frame.pack(fill=tk.BOTH, expand=True)  # Show the main content frame
        
        # Update paths and reset page if needed
        if not force_page:
            self.current_paths = paths
            self.current_page = 0
        
        # Sort paths by confidence score if they are from a category
        category_paths = self.current_paths
        if category_paths and category_paths[0] in self.confidence_scores:
            category_paths = sorted(category_paths, key=lambda x: self.confidence_scores[x], reverse=True)
            self.current_paths = category_paths

        # Calculate page slice
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.current_paths))
        page_paths = self.current_paths[start_idx:end_idx]
        
        # Update navigation controls
        self.update_page_controls()
        
        # Show thumbnails for current page
        self.selected_check_vars = []
        for idx, img_path in enumerate(page_paths):
            try:
                thumb_size = (240, 180)
                cache_key = (img_path, thumb_size)
                if cache_key in self.image_cache:
                    img_tk = self.image_cache[cache_key]
                else:
                    img = Image.open(img_path).resize(thumb_size)
                    img_tk = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = img_tk
                self.thumb_imgs.append(img_tk)
                
                # Create frame with simple shadow
                frame = tk.Frame(self.thumbs_frame, bd=0, bg="#f9fafb", highlightbackground="#e0e6ef", highlightthickness=2)
                frame.grid(row=idx//5, column=idx%5, padx=12, pady=12)
                
                # Simple shadow effect
                shadow_frame = tk.Frame(frame, bg="#e0e6ef", width=240, height=180)
                shadow_frame.place(x=4, y=4)
                
                lbl_img = tk.Label(frame, image=img_tk, bg="#f9fafb")
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_img.bind('<Double-Button-1>', lambda e, p=img_path: self.open_full_image(p))
                
                # Simple hover effects
                def on_enter(ev, f=frame, s=shadow_frame):
                    f.config(bg="#e3eafc", highlightbackground="#a5d8fa")
                    s.place(x=2, y=2)
                def on_leave(ev, f=frame, s=shadow_frame):
                    f.config(bg="#f9fafb", highlightbackground="#e0e6ef")
                    s.place(x=4, y=4)
                
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                lbl_img.bind("<Enter>", on_enter)
                lbl_img.bind("<Leave>", on_leave)
                
                # Text frame for filename and confidence
                text_frame = tk.Frame(frame, bg="#f9fafb")
                text_frame.pack(fill=tk.X, pady=4)
                
                var = tk.BooleanVar()
                chk = tk.Checkbutton(text_frame, text=os.path.basename(img_path), variable=var,
                                   command=lambda v=var, p=img_path: self.on_image_check(v, p),
                                   font=("Arial", 10), bg="#f9fafb", activebackground="#e3eafc",
                                   selectcolor="#a5d8fa", bd=0, highlightthickness=0)
                chk.pack(side=tk.LEFT)
                
                if img_path in self.confidence_scores:
                    conf_text = f"{self.confidence_scores[img_path]:.2f}"
                    conf_label = tk.Label(text_frame, text=conf_text, font=("Arial", 9),
                                        bg="#f9fafb", fg="#666666")
                    conf_label.pack(side=tk.RIGHT, padx=4)
                
                self.selected_check_vars.append((var, img_path))
                var.trace_add('write', lambda *args: self.update_clean_btn_label(self.count_selected_photos()))
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
                continue
        
        # Update zoom controls
        self.update_zoom_controls()
        
        # Reset cursor and update view
        self.root.config(cursor="")
        self.thumbs_frame.config(cursor="")
        self.thumb_canvas.update_idletasks()
        self.thumb_canvas.yview_moveto(0)
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Identifier")
        self.root.geometry("800x600")
        self.folder = None
        self.images = []
        self.current = 0
        self.people_images = []
        self.screenshot_images = []
        self.current_list = "all"  # can be "all", "people", "screenshot"
        self.image_cache = {}  # path -> PhotoImage
        self.confidence_scores = {}  # path -> confidence score
        # Paging variables
        self.page_size = 50  # images per page
        self.current_page = 0
        self.current_paths = []
        
        # Thumbnail size configuration
        self.thumb_size = (240, 180)  # Default size
        self.min_thumb_size = (60, 45)  # Minimum size
        self.max_thumb_size = (580, 360)  # Maximum size
        
        self.setup_ui()

    def setup_ui(self):
        import tkinter.ttk as ttk
        self.root.configure(bg="#f7fafc")

        # Header with soft gradient
        header = tk.Canvas(self.root, height=60, bg="#e3eafc", highlightthickness=0)
        header.pack(fill=tk.X)
        header.create_rectangle(0, 0, 2000, 60, fill="#e3eafc", outline="")
        header.create_rectangle(0, 0, 2000, 30, fill="#c7d6f7", outline="")
        header.create_text(32, 30, anchor="w", text="PhotoSift - Screenshot Identifier", font=("Segoe UI", 22, "bold"), fill="#3a4a63")

        # Top frame for folder selection
        frm = tk.Frame(self.root, bg="#f7fafc")
        frm.pack(fill=tk.X, padx=24, pady=(14, 18))
        style_btn = {"font": ("Segoe UI", 12, "bold"), "bg": "#e0e6ef", "activebackground": "#d0d7e6", "activeforeground": "#3a4a63", "bd": 0, "relief": tk.FLAT, "cursor": "hand2", "highlightthickness": 0}
        btn = tk.Button(frm, text="Select Folder", command=self.select_folder, **style_btn)
        btn.pack(side=tk.LEFT, padx=(0, 16), ipadx=10, ipady=4)
        btn.bind("<Enter>", lambda e: btn.config(bg="#d0d7e6"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#e0e6ef"))
        self.lbl_folder = tk.Label(frm, text="No folder selected", bg="#f7fafc", font=("Segoe UI", 12, "italic"), fg="#6b7280")
        self.lbl_folder.pack(side=tk.LEFT, padx=12)

        # Main frame for tree and image
        main_frame = tk.Frame(self.root, bg="#f7fafc")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        # Sidebar (Treeview) with rounded corners and soft shadow
        sidebar = tk.Frame(main_frame, bg="#e9ecf2", width=220, height=500, bd=0, highlightbackground="#dbeafe", highlightthickness=2)
        sidebar.pack_propagate(False)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), pady=6)
        # Simulate a soft drop shadow for sidebar (right side)
        sidebar_shadow = tk.Frame(main_frame, bg="#e0e6ef", width=8)
        sidebar_shadow.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 22), pady=12)
        tree_label = tk.Label(sidebar, text="Categories", bg="#e9ecf2", font=("Segoe UI", 13, "bold"), anchor="w", fg="#3a4a63")
        tree_label.pack(fill=tk.X, padx=14, pady=(16, 6))
        tree_frame = tk.Frame(sidebar, bg="#e9ecf2")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 14))
        tree_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_xscroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, xscrollcommand=tree_xscroll.set, selectmode="extended")
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Card-like main content area with rounded corners and shadow
        card = tk.Frame(main_frame, bg="#f9fafb", bd=0, highlightbackground="#dbeafe", highlightthickness=2)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0), pady=0)
        
        # Add zoom controls
        zoom_frame = tk.Frame(card, bg="#f9fafb")
        zoom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add zoom out button
        self.zoom_out_btn = tk.Button(zoom_frame, text="🔍-", command=self.zoom_out, 
                                    font=("Segoe UI", 12), bg="#e0e6ef", activebackground="#d0d7e6",
                                    bd=0, relief=tk.FLAT, cursor="hand2", highlightthickness=0)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5, ipadx=8, ipady=2)
        
        # Add zoom in button
        self.zoom_in_btn = tk.Button(zoom_frame, text="🔍+", command=self.zoom_in,
                                   font=("Segoe UI", 12), bg="#e0e6ef", activebackground="#d0d7e6",
                                   bd=0, relief=tk.FLAT, cursor="hand2", highlightthickness=0)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5, ipadx=8, ipady=2)
        
        # Add zoom level label
        self.zoom_label = tk.Label(zoom_frame, text="Zoom: 100%", bg="#f9fafb", font=("Segoe UI", 10))
        self.zoom_label.pack(side=tk.LEFT, padx=10)
        
        # Simulate a soft drop shadow for card (right side)
        card_shadow = tk.Frame(main_frame, bg="#e0e6ef", width=12)
        card_shadow.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 0), pady=18)

        # Right frame for selected thumbnails with buttons (inside card)
        self.right_frame = tk.Frame(card, bg="#f9fafb")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Clean button frame (right side)
        clean_btn_frame = tk.Frame(self.right_frame, bg="#f9fafb")
        clean_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=16)
        # Select All button
        self.select_all_btn = tk.Button(clean_btn_frame, text="Select All", font=("Segoe UI", 12, "bold"), bg="#a5d8fa", fg="#3a4a63", activebackground="#74c0fc", activeforeground="#22223b", bd=0, relief=tk.FLAT, padx=20, pady=10, cursor="hand2", highlightthickness=0)
        self.select_all_btn.config(command=self.select_all_photos, borderwidth=0, highlightbackground="#a5d8fa", highlightcolor="#a5d8fa")
        self.select_all_btn.pack(side=tk.TOP, anchor="ne", pady=(12, 10), ipadx=8, ipady=4)
        self.select_all_btn.bind("<Enter>", lambda e: self.select_all_btn.config(bg="#b6e0fe"))
        self.select_all_btn.bind("<Leave>", lambda e: self.select_all_btn.config(bg="#a5d8fa"))

        self.clean_btn_var = tk.StringVar()
        self.clean_btn_var.set("Clean (0)")
        self.clean_btn = tk.Button(clean_btn_frame, textvariable=self.clean_btn_var, font=("Segoe UI", 12, "bold"), bg="#ffb4a2", fg="#3a4a63", activebackground="#ff7f51", activeforeground="#fff", bd=0, relief=tk.FLAT, padx=20, pady=10, cursor="hand2", highlightthickness=0)
        self.clean_btn.config(command=self.clean_selected_photos, borderwidth=0, highlightbackground="#ffb4a2", highlightcolor="#ffb4a2")
        self.clean_btn.pack(side=tk.TOP, anchor="ne", pady=(0,0), ipadx=8, ipady=4)
        self.clean_btn.bind("<Enter>", lambda e: self.clean_btn.config(bg="#ffd6c0"))
        self.clean_btn.bind("<Leave>", lambda e: self.clean_btn.config(bg="#ffb4a2"))

        # Page navigation controls
        self.page_frame = tk.Frame(self.right_frame, bg="#f9fafb")
        self.page_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))
        
        nav_btn_style = {"font": ("Segoe UI", 11), "bg": "#e0e6ef", "fg": "#3a4a63",
                         "activebackground": "#d0d7e6", "activeforeground": "#3a4a63",
                         "bd": 0, "padx": 15, "pady": 5, "cursor": "hand2"}
        
        self.prev_page_btn = tk.Button(self.page_frame, text="← Previous", command=self.prev_page, **nav_btn_style)
        self.prev_page_btn.pack(side=tk.LEFT)
        
        self.page_label = tk.Label(self.page_frame, text="Page 1", font=("Segoe UI", 11), bg="#f9fafb", fg="#3a4a63")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_page_btn = tk.Button(self.page_frame, text="Next →", command=self.next_page, **nav_btn_style)
        self.next_page_btn.pack(side=tk.LEFT)
        
        self.page_frame.pack_forget()  # Hide initially
        
        # Main container for page controls and thumbnails
        self.content_frame = tk.Frame(self.right_frame, bg="#f9fafb")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Page navigation controls - centered at top
        self.page_frame = tk.Frame(self.content_frame, bg="#f9fafb")
        self.page_frame.pack(fill=tk.X, padx=10, pady=(10, 20))
        
        # Center container for navigation
        nav_center = tk.Frame(self.page_frame, bg="#f9fafb")
        nav_center.pack(expand=True, fill=tk.X)
        
        # Create a nested frame for the buttons to ensure center alignment
        nav_buttons = tk.Frame(nav_center, bg="#f9fafb")
        nav_buttons.pack(expand=True, anchor="center")
        
        nav_btn_style = {"font": ("Segoe UI", 11), "bg": "#e0e6ef", "fg": "#3a4a63",
                         "activebackground": "#d0d7e6", "activeforeground": "#3a4a63",
                         "bd": 0, "padx": 15, "pady": 5, "cursor": "hand2"}
        
        self.prev_page_btn = tk.Button(nav_buttons, text="\u2190 Previous", command=self.prev_page, **nav_btn_style)
        self.prev_page_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.page_label = tk.Label(nav_buttons, text="Page 1", font=("Segoe UI", 11), bg="#f9fafb", fg="#3a4a63")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_page_btn = tk.Button(nav_buttons, text="Next \u2192", command=self.next_page, **nav_btn_style)
        self.next_page_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Thumbnail container
        self.thumb_container = tk.Frame(self.content_frame, bg="#f9fafb")
        self.thumb_container.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Thumbnail canvas and scrollbar
        self.thumb_canvas = tk.Canvas(self.thumb_container, bg="#f9fafb", highlightthickness=0, bd=0)
        self.thumb_scrollbar = tk.Scrollbar(self.thumb_container, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.content_frame.pack_forget()  # Hide initially
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg="#f9fafb")
        self.thumb_canvas.create_window((0,0), window=self.thumbs_frame, anchor="nw")
        # Configure frame for layout updates
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_canvas.bind("<Configure>", self.on_canvas_configure)
        self.thumb_imgs = []
        self.right_frame.pack_forget()  # Hide initially

        # Center frame for image and controls (inside card)
        self.center_frame = tk.Frame(card, bg="#f9fafb")
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.img_panel = tk.Label(self.center_frame, bg="#f9fafb", bd=0, highlightbackground="#b0b6c6", highlightthickness=1, relief=tk.GROOVE)
        self.img_panel.pack(pady=(44, 16), ipadx=6, ipady=6)
        self.lbl_result = tk.Label(self.center_frame, text="", font=("Segoe UI", 17, "bold"), bg="#f9fafb", fg="#3a4a63")
        self.lbl_result.pack(pady=10)

        # Status bar at bottom, full width
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=0, relief=tk.FLAT, anchor=tk.W, bg="#c7d6f7", fg="#3a4a63", font=("Segoe UI", 11))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(0,2))

    def on_canvas_configure(self, event=None):
        # Update scroll region
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
        
        # Only refresh layout if width changed significantly
        if event and hasattr(self, 'last_width') and abs(event.width - self.last_width) < 50:
            return
            
        self.last_width = event.width if event else self.thumb_canvas.winfo_width()
        
        # If we have current paths displayed, refresh the layout
        if hasattr(self, 'current_paths') and self.current_paths:
            self.show_selected_thumbnails(self.current_paths, force_page=True)
    
    def show_progress_window(self, total):
        # Create progress window
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Processing Images")
        self.progress_window.geometry("400x150")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Center the progress window
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure progress window
        self.progress_window.configure(bg="#f7fafc")
        frame = tk.Frame(self.progress_window, bg="#f7fafc", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Progress label
        self.progress_label = tk.Label(frame, text="Initializing...", font=("Segoe UI", 11), bg="#f7fafc")
        self.progress_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", thickness=15, background='#3399ff')
        self.progress_bar = ttk.Progressbar(frame, style="Custom.Horizontal.TProgressbar", 
                                          length=360, mode='determinate', 
                                          maximum=total, variable=self.progress_var)
        self.progress_bar.pack(pady=(0, 10))
        
        # Detailed status
        self.progress_detail = tk.Label(frame, text="", font=("Segoe UI", 10), bg="#f7fafc", fg="#666666")
        self.progress_detail.pack()

    def update_progress(self, current, total, status_text, detail_text):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_var.set(current)
            self.progress_label.config(text=status_text)
            self.progress_detail.config(text=detail_text)
            self.progress_window.update_idletasks()

    def close_progress(self):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.lbl_folder.config(text=folder)
            # Walk through directory but exclude Trash folder
            self.images = []
            for dp, dn, filenames in os.walk(folder):
                # Skip the Trash directory and its subdirectories
                if "Trash" in dp.split(os.sep):
                    continue
                    
                # Add valid images to the list
                for f in filenames:
                    if os.path.splitext(f)[1].lower() in IMG_EXT:
                        self.images.append(os.path.join(dp, f))
            self.people_images = []
            self.screenshot_images = []
            self.image_labels = {}  # path -> label
            total = len(self.images)
            
            # Show progress window
            self.root.after(0, self.show_progress_window, total)
            self.status_bar.config(bg="#3399ff", fg="white")
            self.status_var.set(f"Processing 0/{total} images (0%)...")
            self.root.update_idletasks()

            def process_images():
                from ImageClassification import classify_people_vs_screenshot_batch
                batch_size = 64  # Increase batch size for better GPU utilization
                processed = 0
                
                for start in range(0, total, batch_size):
                    end = min(start + batch_size, total)
                    batch_paths = self.images[start:end]
                    percent = int((end/total)*100) if total else 100
                    status_text = f"Processing images... ({percent}%)"
                    detail_text = f"Processing {start+1}-{end} of {total} images"
                    
                    # Update both progress window and status bar
                    self.root.after(0, self.update_progress, end, total, status_text, detail_text)
                    self.root.after(0, self.status_var.set, f"Processing images {start+1}-{end}/{total} ({percent}%)")
                    self.root.after(0, self.status_bar.config, {"bg": "#3399ff", "fg": "white"})
                    
                    batch_results = classify_people_vs_screenshot_batch(batch_paths)
                    for p, result in zip(batch_paths, batch_results):
                        if result is None:
                            print(f"[WARN] Skipping image due to load/classify failure: {p}")
                            continue
                        label, conf, _ = result
                        self.image_labels[p] = label
                        self.confidence_scores[p] = conf
                        if label == "people":
                            self.people_images.append(p)
                        elif label == "screenshot":
                            self.screenshot_images.append(p)
                    
                    # Sort the lists by confidence score
                    self.people_images.sort(key=lambda x: self.confidence_scores[x], reverse=True)
                    self.screenshot_images.sort(key=lambda x: self.confidence_scores[x], reverse=True)
                    
                    processed += len(batch_paths)
                
                # Processing complete
                people_count = len(self.people_images)
                screenshot_count = len(self.screenshot_images)
                final_status = f"Completed! Found {people_count} people and {screenshot_count} screenshots"
                self.root.after(0, self.update_progress, total, total, "Processing Complete!", final_status)
                self.root.after(0, self.status_var.set, f"Done processing {total} images. (100%) | People: {people_count} | Screenshot: {screenshot_count}")
                self.root.after(0, self.status_bar.config, {"bg": "#33cc33", "fg": "white"})
                
                # Update UI
                self.current = 0
                self.current_list = "all"
                self.root.after(0, self.populate_tree)
                if self.images:
                    self.root.after(0, self.show_img)
                else:
                    self.root.after(0, lambda: messagebox.showinfo("No Images", "No images found in folder."))
                
                # Close progress window after a short delay
                self.root.after(1500, self.close_progress)
                
            threading.Thread(target=process_images, daemon=True).start()

    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        people_count = len(self.people_images)
        screenshot_count = len(self.screenshot_images)
        people_node = self.tree.insert("", "end", text=f"People ({people_count})", open=True)
        for p in self.people_images:
            self.tree.insert(people_node, "end", text=os.path.basename(p), values=(p,))
        screenshot_node = self.tree.insert("", "end", text=f"Screenshot ({screenshot_count})", open=True)
        for p in self.screenshot_images:
            self.tree.insert(screenshot_node, "end", text=os.path.basename(p), values=(p,))
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        # If Screenshot node is selected, show all screenshot images
        selected_paths = []
        for sel in selected:
            item = self.tree.item(sel)
            if item['text'].startswith('Screenshot') and not item['values']:
                # Screenshot node selected, show all screenshot images
                selected_paths.extend(self.screenshot_images)
            elif 'values' in item and item['values']:
                selected_paths.append(item['values'][0])
        if selected_paths:
            self.center_frame.pack_forget()
            self.current_page = 0  # Reset to first page
            self.show_selected_thumbnails(selected_paths)
        else:
            # Fallback to single image view if no images selected
            item = self.tree.item(selected[0])
            if 'values' in item and item['values']:
                path = item['values'][0]
                if self.image_labels[path] == "people":
                    self.current_list = "people"
                    self.current = self.people_images.index(path)
                elif self.image_labels[path] == "screenshot":
                    self.current_list = "screenshot"
                    self.current = self.screenshot_images.index(path)
                else:
                    self.current_list = "all"
                    self.current = self.images.index(path)
                self.right_frame.pack_forget()
                self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.show_img()
    def animate_button_click(self, button):
        # Quick visual feedback without delays
        button.config(bg="#a5d8fa", fg="#ffffff")
        self.root.after(50, lambda: button.config(bg="#e0e6ef", fg="#3a4a63"))
    
    def next_page(self):
        if not hasattr(self, 'current_paths') or not self.current_paths:
            return
        
        next_page = self.current_page + 1
        if next_page * self.page_size < len(self.current_paths):
            self.current_page = next_page
            # Disable buttons during update to prevent rapid clicks
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            self.root.after(1, lambda: self.show_selected_thumbnails(self.current_paths, force_page=True))
    
    def prev_page(self):
        if not hasattr(self, 'current_paths') or not self.current_paths:
            return
            
        if self.current_page > 0:
            self.current_page -= 1
            # Disable buttons during update to prevent rapid clicks
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            self.root.after(1, lambda: self.show_selected_thumbnails(self.current_paths, force_page=True))
    
    def zoom_in(self):
        current_width, current_height = self.thumb_size
        new_width = min(int(current_width * 1.1), self.max_thumb_size[0])
        new_height = min(int(current_height * 1.1), self.max_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.show_selected_thumbnails(self.current_paths, force_page=True)
            
    def zoom_out(self):
        current_width, current_height = self.thumb_size
        new_width = max(int(current_width * 0.9), self.min_thumb_size[0])
        new_height = max(int(current_height * 0.9), self.min_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            self.show_selected_thumbnails(self.current_paths, force_page=True)
            
    def update_zoom_controls(self):
        can_zoom_in = self.thumb_size[0] < self.max_thumb_size[0]
        can_zoom_out = self.thumb_size[0] > self.min_thumb_size[0]
        self.zoom_in_btn.config(state=tk.NORMAL if can_zoom_in else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if can_zoom_out else tk.DISABLED)
    
    def update_page_controls(self):
        if not hasattr(self, 'current_paths') or not self.current_paths:
            self.page_label.config(text="Page 0 of 0")
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            return
            
        total_pages = max(1, (len(self.current_paths) - 1) // self.page_size + 1)
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        
        # Update button states
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        next_enabled = (self.current_page + 1) * self.page_size < len(self.current_paths)
        self.next_page_btn.config(state=tk.NORMAL if next_enabled else tk.DISABLED)
    
    def animate_fade(self, widget, start_alpha, end_alpha, steps=10, interval=20):
        # Helper function for fade animation
        current = float(start_alpha)
        step = (float(end_alpha) - float(start_alpha)) / steps
        
        def update_alpha():
            nonlocal current
            current += step
            if (step > 0 and current <= float(end_alpha)) or (step < 0 and current >= float(end_alpha)):
                widget.configure(bg=self.blend_colors("#f9fafb", "#ffffff", current))
                self.root.after(interval, update_alpha)
        
        update_alpha()
    
    def blend_colors(self, color1, color2, factor):
        # Helper function to blend two colors
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def show_selected_thumbnails(self, paths, force_page=False):
        # Clear previous thumbnails immediately without fade
        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.img_panel.pack_forget()
        self.lbl_result.pack_forget()
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.content_frame.pack(fill=tk.BOTH, expand=True)  # Show the main content frame

        self.center_frame.pack_forget()
        self.selected_check_vars = []
        self.update_clean_btn_label(0)
        
        # Update paths and reset page if needed
        if not force_page:
            self.current_paths = paths
            self.current_page = 0
        
        # Sort paths by confidence score if they are from a category
        category_paths = self.current_paths
        if category_paths and category_paths[0] in self.confidence_scores:
            category_paths = sorted(category_paths, key=lambda x: self.confidence_scores[x], reverse=True)
            self.current_paths = category_paths

        # Calculate page slice
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.current_paths))
        page_paths = self.current_paths[start_idx:end_idx]
        
        # Update navigation controls
        self.update_page_controls()
        
        # Configure grid for proper spacing
        cols = self.calculate_columns()
        for i in range(cols):
            self.thumbs_frame.grid_columnconfigure(i, weight=1)
        
        # Show thumbnails for current page
        for idx, img_path in enumerate(page_paths):
            try:
                cache_key = (img_path, self.thumb_size)
                if cache_key in self.image_cache:
                    img_tk = self.image_cache[cache_key]
                else:
                    img = Image.open(img_path).resize(self.thumb_size)
                    img_tk = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = img_tk
                self.thumb_imgs.append(img_tk)
                
                # Update zoom level indicator
                base_width = 240  # Reference width
                zoom_level = int((self.thumb_size[0] / base_width) * 100)
                self.zoom_label.config(text=f"Zoom: {zoom_level}%")
                
                # Calculate layout position
                cols = self.calculate_columns()
                
                # Create animated frame with shadow effect
                frame = tk.Frame(self.thumbs_frame, bd=0, bg="#f9fafb", highlightbackground="#e0e6ef", highlightthickness=2)
                frame.grid(row=idx//cols, column=idx%cols, padx=12, pady=12, sticky='nsew')
                
                # Add shadow frame behind for depth effect
                shadow_frame = tk.Frame(frame, bg="#e0e6ef", width=self.thumb_size[0], height=self.thumb_size[1])
                shadow_frame.place(x=4, y=4)  # Place shadow slightly offset
                
                lbl_img = tk.Label(frame, image=img_tk, bg="#f9fafb")
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_img.bind('<Double-Button-1>', lambda e, p=img_path: self.open_full_image(p))
                
                # Enhanced hover animations
                def on_enter(ev, f=frame, s=shadow_frame):
                    # Instant color change with quick shadow animation
                    f.config(bg="#e3eafc", highlightbackground="#a5d8fa")
                    s.place(x=0, y=0)  # Quick lift effect
                    
                def on_leave(ev, f=frame, s=shadow_frame):
                    # Instant color change with quick shadow reset
                    f.config(bg="#f9fafb", highlightbackground="#e0e6ef")
                    s.place(x=4, y=4)  # Quick drop effect
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                lbl_img.bind("<Enter>", on_enter)
                lbl_img.bind("<Leave>", on_leave)
                var = tk.BooleanVar()
                # Create frame for text (filename and confidence)
                text_frame = tk.Frame(frame, bg="#f9fafb")
                text_frame.pack(fill=tk.X, pady=4)
                
                # Filename checkbox
                chk = tk.Checkbutton(text_frame, text=os.path.basename(img_path), variable=var, 
                                   command=lambda v=var, p=img_path: self.on_image_check(v, p), 
                                   font=("Arial", 10), bg="#f9fafb", activebackground="#e3eafc", 
                                   selectcolor="#a5d8fa", bd=0, highlightthickness=0)
                chk.pack(side=tk.LEFT)
                
                # Confidence score if available
                if img_path in self.confidence_scores:
                    conf_text = f"{self.confidence_scores[img_path]:.2f}"
                    conf_label = tk.Label(text_frame, text=conf_text, font=("Arial", 9), 
                                        bg="#f9fafb", fg="#666666")
                    conf_label.pack(side=tk.RIGHT, padx=4)
                self.selected_check_vars.append((var, img_path))
                var.trace_add('write', lambda *args: self.update_clean_btn_label(self.count_selected_photos()))
            except Exception:
                continue
        self.thumb_canvas.update_idletasks()
        self.thumb_canvas.yview_moveto(0)

    def calculate_columns(self):
        # Get the actual width of the canvas
        canvas_width = self.thumb_canvas.winfo_width()
        if not canvas_width:
            # If not yet realized, get parent's width
            canvas_width = self.thumb_canvas.master.winfo_width() or 800
        
        # Calculate space needed for each thumbnail including padding
        thumb_space = self.thumb_size[0] + 24  # thumbnail width + padding
        
        # Calculate number of columns that can fit
        return max(1, canvas_width // thumb_space)
    
    def count_selected_photos(self):
        return sum(var.get() for var, _ in self.selected_check_vars)

    def update_clean_btn_label(self, count):
        self.clean_btn_var.set(f"Clean ({count})")

    def clean_selected_photos(self):
        # Get selected photos
        selected = [img_path for var, img_path in self.selected_check_vars if var.get()]
        if not selected:
            messagebox.showinfo("Clean", "No photos selected.")
            return


        # Create Trash directory if it doesn't exist
        if not self.folder:
            messagebox.showerror("Error", "No folder selected.")
            return

        trash_dir = os.path.join(self.folder, "Trash")
        try:
            os.makedirs(trash_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create Trash directory:\n{str(e)}")
            return

        # Move files to trash
        moved_count = 0
        failed_files = []
        
        for img_path in selected:
            try:
                # Generate unique filename in case of duplicates
                base_name = os.path.basename(img_path)
                name, ext = os.path.splitext(base_name)
                target_path = os.path.join(trash_dir, base_name)
                counter = 1
                
                while os.path.exists(target_path):
                    target_path = os.path.join(trash_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                # Move the file
                shutil.move(img_path, target_path)
                moved_count += 1
                
                # Remove from data structures
                if img_path in self.images:
                    self.images.remove(img_path)
                if img_path in self.people_images:
                    self.people_images.remove(img_path)
                if img_path in self.screenshot_images:
                    self.screenshot_images.remove(img_path)
                if img_path in self.image_labels:
                    del self.image_labels[img_path]
                if img_path in self.confidence_scores:
                    del self.confidence_scores[img_path]
                if img_path in self.image_cache:
                    del self.image_cache[img_path]
                    
            except Exception as e:
                print(f"Failed to move {img_path}: {str(e)}")
                failed_files.append(base_name)

        # Show simple popup message
        try:
            popup = tk.Toplevel()
            popup.title("Clean Complete")
            
            # Make the window float on top
            popup.lift()
            popup.attributes('-topmost', True)
            
            # Basic window setup
            window_width = 300
            window_height = 100
            
            # Get the position of the main window
            main_window_x = self.root.winfo_x()
            main_window_y = self.root.winfo_y()
            main_window_width = self.root.winfo_width()
            main_window_height = self.root.winfo_height()
            
            # Calculate position (centered on main window)
            position_x = main_window_x + (main_window_width - window_width) // 2
            position_y = main_window_y + (main_window_height - window_height) // 2
            
            # Set window geometry
            popup.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
            
            # Configure basic style
            popup.configure(bg='white')
            
            # Create message
            if failed_files:
                message = f"Moved {moved_count} photos to Trash.\nFailed: {len(failed_files)} files"
                fg_color = "red"
            else:
                message = f"Successfully moved {moved_count} photos to Trash"
                fg_color = "blue"
            
            # Add message label
            label = tk.Label(popup, text=message, bg='white', fg=fg_color, 
                           font=("Segoe UI", 11))
            label.pack(expand=True)
            
            # Force the window to update and show
            popup.update()
            
            # Schedule destruction
            popup.after(2000, popup.destroy)
            
        except Exception as e:
            print(f"Error showing popup: {str(e)}")
            messagebox.showinfo("Clean Complete", 
                              f"Moved {moved_count} photos to Trash")
        
        # Auto-close after 1 second
        popup.after(1000, popup.destroy)

        # Refresh UI
        self.populate_tree()  # Update the category tree
        
        # If we're in thumbnail view, refresh it
        if self.current_paths:
            # Remove cleaned images from current_paths
            self.current_paths = [p for p in self.current_paths if p not in selected]
            if self.current_paths:
                self.show_selected_thumbnails(self.current_paths, force_page=True)
            else:
                # No images left in current view
                self.right_frame.pack_forget()
                self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.content_frame.pack_forget()

    def open_full_image(self, img_path):
        top = tk.Toplevel(self.root)
        top.title(os.path.basename(img_path))
        img = Image.open(img_path)
        img_tk = ImageTk.PhotoImage(img)
        lbl = tk.Label(top, image=img_tk)
        lbl.image = img_tk
        lbl.pack()
        self.thumb_canvas.update_idletasks()
        self.thumb_canvas.yview_moveto(0)

    def on_image_check(self, var, path, frame=None):
        # Pulse animation when checking/unchecking
        if frame:
            original_color = frame.cget('bg')
            highlight = "#a5d8fa" if var.get() else "#ffb4a2"
            shadow_intensity = 4 if var.get() else 2
            
            def animate_pulse():
                # Quick pulse animation
                frame.config(bg=highlight)
                for i in range(shadow_intensity, -1, -1):
                    if hasattr(frame, 'shadow_frame'):
                        frame.shadow_frame.place(x=i, y=i)
                    self.root.after(10)
                    self.root.update_idletasks()
                self.root.after(100, lambda: frame.config(bg=original_color))
            
            animate_pulse()
        
        print(f"Selected: {os.path.basename(path)}")
        #messagebox.showinfo("Image Selected", f"Selected: {os.path.basename(path)}")

    def show_img(self):
        img_list = self.get_current_list()
        if not img_list:
            self.img_panel.config(image=None)
            self.img_panel.image = None
            self.lbl_result.config(text="No images in this category.")
            return
        path = img_list[self.current]
        # Use cache if available
        main_size = (800, 600)
        cache_key = (path, main_size)
        if cache_key in self.image_cache:
            img_tk = self.image_cache[cache_key]
        else:
            img = Image.open(path).resize(main_size)
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = img_tk
        self.img_panel.config(image=img_tk)
        self.img_panel.image = img_tk
        label, conf, _ = classify_people_vs_screenshot(path)
        self.lbl_result.config(text=f"{os.path.basename(path)}: {label} ({conf:.2f})")

    # Removed next_img and prev_img methods as requested

    def get_current_list(self):
        if self.current_list == "all":
            return self.images
        elif self.current_list == "people":
            return self.people_images
        elif self.current_list == "screenshot":
            return self.screenshot_images
        return []

    # Removed category button methods as requested

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
