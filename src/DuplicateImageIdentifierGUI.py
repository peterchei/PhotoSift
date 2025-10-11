import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
from DuplicateImageIdentifier import group_similar_images_clip, IMG_EXT

class ToolTip:
    """
    Create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class DuplicateImageIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoSift - Duplicate Image Identifier")
        self.root.state('zoomed')  # Start maximized
        
        # Modern color scheme (same as ImageClassifierGUI)
        self.colors = {
            'bg_primary': '#1e293b',      # Dark blue background
            'bg_secondary': '#334155',    # Secondary dark blue
            'bg_card': '#475569',         # Card background
            'accent': '#3b82f6',          # Blue accent
            'text_primary': '#f1f5f9',    # White text
            'text_secondary': '#94a3b8',  # Light gray text
            'success': '#10b981',         # Green
            'warning': '#f59e0b',         # Orange
            'danger': '#ef4444'           # Red
        }
        
        self.folder = None
        self.groups = []
        
        # Selection and confidence tracking
        self.selected_check_vars = []  # List of (checkbox_var, image_path) tuples
        self.similarity_scores = {}  # path -> similarity score for duplicates
        self._updating_bulk_selection = False  # Flag to prevent callback loops during bulk operations
        
        # Thumbnail size configuration for zoom functionality
        self.thumb_size = (180, 135)  # Default size for single group view
        self.multi_thumb_size = (150, 120)  # Default size for multi-group view
        self.min_thumb_size = (80, 60)  # Minimum size
        self.max_thumb_size = (300, 225)  # Maximum size
        
        self.setup_ui()
        self.apply_modern_styling()
        self.create_status_bar()

    def setup_ui(self):
        # Configure main window
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Create modern header
        self.create_modern_header()
        
        # Create main content area
        self.create_modern_content()

    def create_modern_header(self):
        # Modern header with better typography
        header = tk.Frame(self.root, bg=self.colors['bg_primary'], height=80)
        header.pack(fill=tk.X, padx=20, pady=(20, 0))
        header.pack_propagate(False)
        
        # App title section (left side)
        title_frame = tk.Frame(header, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(title_frame, 
                              text="PhotoSift", 
                              font=("Segoe UI", 28, "bold"),
                              bg=self.colors['bg_primary'], 
                              fg=self.colors['text_primary'])
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Duplicate Image Identifier", 
                                 font=("Segoe UI", 14),
                                 bg=self.colors['bg_primary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor="w")
        
        # Header buttons frame (right side)
        header_buttons = tk.Frame(header, bg=self.colors['bg_primary'])
        header_buttons.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Modern trash button with icon
        self.trash_btn_var = tk.StringVar(value="🗑️ 0")
        self.trash_btn = tk.Button(header_buttons, 
                                  textvariable=self.trash_btn_var, 
                                  command=self.open_trash_folder,
                                  font=("Segoe UI", 12, "bold"),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_primary'],
                                  activebackground=self.colors['bg_card'],
                                  activeforeground=self.colors['text_primary'],
                                  bd=0, relief=tk.FLAT, cursor="hand2",
                                  padx=15, pady=8)
        self.trash_btn.pack(side=tk.RIGHT, padx=(10, 0))

    def create_modern_content(self):
        # Main content container
        content = tk.Frame(self.root, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create sidebar
        self.create_modern_sidebar(content)
        
        # Create main area
        self.create_modern_main_area(content)
    
    def create_modern_sidebar(self, parent):
        # Modern sidebar
        sidebar = tk.Frame(parent, bg=self.colors['bg_secondary'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20), pady=(20, 0))
        sidebar.pack_propagate(False)
        
        # Folder selection section
        folder_section = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        folder_section.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Modern select folder button
        self.select_btn = tk.Button(folder_section, 
                                   text="Select Folder", 
                                   command=self.select_folder,
                                   font=("Segoe UI", 11, "bold"),
                                   bg=self.colors['accent'],
                                   fg=self.colors['text_primary'],
                                   activebackground='#2563eb',
                                   activeforeground=self.colors['text_primary'],
                                   bd=0,
                                   padx=20,
                                   pady=8,
                                   cursor="hand2")
        self.select_btn.pack(fill=tk.X)
        
        # Folder path display
        self.lbl_folder = tk.Label(folder_section, 
                                  text="No folder selected", 
                                  font=("Segoe UI", 10),
                                  bg=self.colors['bg_secondary'], 
                                  fg=self.colors['text_secondary'],
                                  wraplength=240,
                                  justify=tk.LEFT)
        self.lbl_folder.pack(anchor="w", pady=(10, 0))
        
        # Groups section
        groups_section = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        groups_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 0))
        
        tk.Label(groups_section, 
                text="Duplications", 
                font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary']).pack(anchor="w", pady=(0, 10))
        
        # Tree view with modern styling
        tree_container = tk.Frame(groups_section, bg=self.colors['bg_card'])
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars with modern styling
        tree_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, style="Modern.Vertical.TScrollbar")
        tree_xscroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, style="Modern.Horizontal.TScrollbar")
        
        self.tree = ttk.Treeview(tree_container, 
                               yscrollcommand=tree_scroll.set, 
                               xscrollcommand=tree_xscroll.set,
                               style="Modern.Treeview",
                               show="tree",
                               selectmode="extended")
        
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Add placeholder text
        placeholder_id = self.tree.insert("", "end", text="📁 Select a folder to find duplicates", tags=("placeholder",))

    def create_modern_main_area(self, parent):
        # Main area for image display
        main_area = tk.Frame(parent, bg=self.colors['bg_primary'])
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Navigation bar with zoom controls and action buttons
        nav_bar = tk.Frame(main_area, bg=self.colors['bg_primary'], height=60)
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
        
        # Action buttons (right side of nav bar)
        action_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Modern Select All button
        self.select_all_btn = tk.Button(action_frame, 
                                       text="Select All", 
                                       command=self.select_all_groups,
                                       font=("Segoe UI", 12, "bold"),
                                       bg=self.colors['accent'],
                                       fg=self.colors['text_primary'],
                                       activebackground='#2563eb',
                                       bd=0, relief=tk.FLAT, cursor="hand2",
                                       padx=16, pady=8)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Modern Clean button
        self.clean_btn_var = tk.StringVar()
        self.clean_btn_var.set("Clean (0)")
        self.clean_btn = tk.Button(action_frame, 
                                  textvariable=self.clean_btn_var,
                                  command=self.clean_selected_images,
                                  font=("Segoe UI", 12, "bold"),
                                  bg=self.colors['danger'],
                                  fg=self.colors['text_primary'],
                                  activebackground='#dc2626',
                                  bd=0, relief=tk.FLAT, cursor="hand2",
                                  padx=16, pady=8)
        self.clean_btn.pack(side=tk.LEFT)
        
        # Image display area with scrolling
        self.create_image_display_area(main_area)
        
        # Result label
        self.lbl_result = tk.Label(main_area, 
                                  text="Select a group to view duplicates", 
                                  font=("Segoe UI", 16, "bold"),
                                  bg=self.colors['bg_primary'], 
                                  fg=self.colors['text_primary'])
        self.lbl_result.pack(pady=(0, 20))

    def create_image_display_area(self, parent):
        # Container for scrollable image area
        img_container = tk.Frame(parent, bg=self.colors['bg_primary'])
        img_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Canvas for scrolling
        self.img_canvas = tk.Canvas(img_container, 
                                   bg=self.colors['bg_primary'],
                                   highlightthickness=0,
                                   bd=0)
        
        # Modern scrollbar
        img_scrollbar = ttk.Scrollbar(img_container, 
                                    orient="vertical", 
                                    command=self.img_canvas.yview,
                                    style="Modern.Vertical.TScrollbar")
        
        self.img_canvas.configure(yscrollcommand=img_scrollbar.set)
        
        img_scrollbar.pack(side="right", fill="y")
        self.img_canvas.pack(side="left", fill="both", expand=True)
        
        # Frame for images
        self.img_panel = tk.Frame(self.img_canvas, bg=self.colors['bg_primary'])
        self.img_canvas.create_window((0, 0), window=self.img_panel, anchor="nw")
        
        # Bind scrolling
        self.img_panel.bind("<Configure>", self.on_img_frame_configure)
        self.img_canvas.bind("<MouseWheel>", self.on_mousewheel)

    def on_img_frame_configure(self, event):
        self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.img_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show_progress_window(self, total):
        # Create modern progress window
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Processing Images - Duplicate Detection")
        self.progress_window.geometry("450x180")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Center the progress window
        window_width = 450
        window_height = 180
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Modern progress window styling
        self.progress_window.configure(bg=self.colors['bg_primary'])
        frame = tk.Frame(self.progress_window, bg=self.colors['bg_primary'], padx=30, pady=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Modern progress label
        self.progress_label = tk.Label(frame, 
                                      text="Initializing Duplicate Detection...", 
                                      font=("Segoe UI", 13, "bold"), 
                                      bg=self.colors['bg_primary'],
                                      fg=self.colors['text_primary'])
        self.progress_label.pack(pady=(0, 15))
        
        # Modern progress bar
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
        
        # Modern detailed status
        self.progress_detail = tk.Label(frame, 
                                       text="", 
                                       font=("Segoe UI", 11), 
                                       bg=self.colors['bg_primary'], 
                                       fg=self.colors['text_secondary'])
        self.progress_detail.pack()

    def update_progress(self, current, total, status_text, detail_text=""):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_var.set(current)
            self.progress_label.config(text=status_text)
            if detail_text:
                self.progress_detail.config(text=detail_text)
            self.progress_window.update_idletasks()

    def close_progress(self):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()

    def apply_modern_styling(self):
        # Configure TTK styles
        style = ttk.Style()
        
        # Set modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Tree styling
        style.configure("Modern.Treeview",
                       rowheight=28,
                       fieldbackground=self.colors['bg_card'],
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       selectbackground=self.colors['accent'],
                       selectforeground=self.colors['text_primary'],
                       borderwidth=0,
                       relief="flat")
        
        style.map("Modern.Treeview",
                 background=[('selected', self.colors['accent']),
                           ('active', self.colors['bg_secondary'])],
                 foreground=[('selected', self.colors['text_primary']),
                           ('active', self.colors['text_primary'])])
        
        # Scrollbar styling
        style.configure("Modern.Vertical.TScrollbar",
                       background=self.colors['bg_secondary'],
                       troughcolor=self.colors['bg_primary'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_secondary'],
                       darkcolor=self.colors['bg_secondary'],
                       lightcolor=self.colors['bg_secondary'])
        
        style.configure("Modern.Horizontal.TScrollbar",
                       background=self.colors['bg_secondary'],
                       troughcolor=self.colors['bg_primary'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_secondary'],
                       darkcolor=self.colors['bg_secondary'],
                       lightcolor=self.colors['bg_secondary'])

    def create_status_bar(self):
        # Modern status bar at bottom
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=35)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a folder to find duplicates")
        self.status_bar = tk.Label(status_frame, 
                                  textvariable=self.status_var, 
                                  bd=0, relief=tk.FLAT, anchor=tk.W, 
                                  bg=self.colors['bg_secondary'], 
                                  fg=self.colors['text_secondary'], 
                                  font=("Segoe UI", 11))
        self.status_bar.pack(fill=tk.BOTH, expand=True, padx=20)

    def get_similarity_tooltip(self, similarity_score):
        """Generate tooltip text for similarity scores"""
        # Convert similarity score to percentage
        percentage = similarity_score * 100
        
        # Determine similarity level and provide helpful guidance
        if percentage >= 95:
            level = "Perfect Match"
            description = "Nearly identical images - likely exact duplicates or minimal differences"
        elif percentage >= 85:
            level = "Excellent Match"
            description = "Very similar images - likely duplicates with minor variations (quality, size, etc.)"
        elif percentage >= 75:
            level = "Good Match"
            description = "Similar images - may be duplicates or closely related photos"
        elif percentage >= 65:
            level = "Fair Match"
            description = "Moderately similar images - review carefully to determine if duplicates"
        else:
            level = "Poor Match"
            description = "Low similarity - may be false positives or very different images"
        
        return f"{level}\n{percentage:.1f}% Similarity\n\n{description}"

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            # Truncate path if too long
            display_path = folder
            if len(display_path) > 35:
                display_path = "..." + display_path[-32:]
            self.lbl_folder.config(text=display_path, fg=self.colors['text_primary'])
            
            # Clear tree
            self.tree.delete(*self.tree.get_children())
            
            # Get all image files first
            files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                     for f in filenames if os.path.splitext(f)[1].lower() in IMG_EXT]
            total = len(files)
            
            if total == 0:
                self.status_var.set("No images found in selected folder")
                messagebox.showinfo("No Images", "No images found in the selected folder.")
                return
            
            # Clear image panel
            for widget in self.img_panel.winfo_children():
                widget.destroy()
            
            # Show progress window
            self.show_progress_window(total)
            
            # Process in thread
            import threading
            def process():
                try:
                    from DuplicateImageIdentifier import get_clip_embedding_batch, group_similar_images_clip
                    embeddings = {}
                    batch_size = 64
                    
                    # Process images in batches
                    for start in range(0, total, batch_size):
                        end = min(start + batch_size, total)
                        batch_files = files[start:end]
                        percent = int((end/total)*100) if total else 100
                        
                        print(f"[LOG] Processing images {start+1}-{end}/{total} ({percent}%)")
                        
                        # Update progress window and status bar
                        status_text = f"Processing Images ({percent}%)"
                        detail_text = f"Analyzing batch {start+1}-{end} of {total} images..."
                        self.update_progress(end, total, status_text, detail_text)
                        
                        # Update status bar
                        status_bar_text = f"Processing images {start+1}-{end}/{total} ({percent}%)"
                        self.root.after(0, self.status_var.set, status_bar_text)
                        
                        try:
                            batch_embeddings = get_clip_embedding_batch(batch_files)
                            for f, emb in zip(batch_files, batch_embeddings):
                                embeddings[f] = emb
                        except Exception as e:
                            print(f"Error processing batch {start}-{end}: {e}")
                            continue
                    
                    # Update progress for duplicate detection phase
                    self.update_progress(total, total, "Identifying Duplicates...", 
                                       "Comparing image similarities and grouping duplicates...")
                    self.root.after(0, self.status_var.set, "Identifying duplicate groups...")
                    
                    # Define progress callback for duplicate detection
                    def duplicate_progress_callback(current, total_imgs, status_text, detail_text):
                        self.root.after(0, self.update_progress, current, total_imgs, status_text, detail_text)
                        percent = int((current / total_imgs) * 100) if total_imgs > 0 else 100
                        status_bar_text = f"Identifying duplicates: {current}/{total_imgs} ({percent}%)"
                        self.root.after(0, self.status_var.set, status_bar_text)
                    
                    # Get groups and similarity scores
                    result = group_similar_images_clip(folder=folder, embeddings=embeddings, files=files, 
                                                     progress_callback=duplicate_progress_callback, 
                                                     return_scores=True)
                    if isinstance(result, tuple):
                        self.groups, self.similarity_scores = result
                    else:
                        # Fallback for older version
                        self.groups = result
                        self.similarity_scores = {}
                    
                    # Update final status
                    total_duplicates = sum(len(group) - 1 for group in self.groups)
                    final_status = f"Complete! Found {len(self.groups)} images with duplicates"
                    final_detail = f"Processed {total} images - {total_duplicates} total duplicates found"
                    self.update_progress(total, total, final_status, final_detail)
                    
                    # Update status bar with final result
                    final_status_text = f"Done! {len(self.groups)} images have duplicates ({total_duplicates} total) from {total} images (100%)"
                    self.root.after(0, self.status_var.set, final_status_text)
                    self.root.after(0, self.status_bar.config, {"bg": "#33cc33", "fg": "white"})
                    
                    # Update main UI
                    total_duplicates = sum(len(group) - 1 for group in self.groups)
                    self.lbl_result.config(text=f"Found {len(self.groups)} images with duplicates ({total_duplicates} total duplicates)", 
                                         fg=self.colors['success'])
                    self.populate_tree()
                    
                    # Close progress window after a short delay
                    self.root.after(2000, self.close_progress)
                    
                except Exception as e:
                    # Handle errors gracefully
                    error_msg = f"Error during processing: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    
                    self.update_progress(0, total, "Processing Failed", error_msg)
                    self.lbl_result.config(text="Processing failed. Check console for details.", 
                                         fg=self.colors['danger'])
                    
                    # Update status bar with error
                    self.root.after(0, self.status_var.set, f"Processing failed: {str(e)}")
                    self.root.after(0, self.status_bar.config, {"bg": "#cc3333", "fg": "white"})
                    
                    # Close progress window after error
                    self.root.after(3000, self.close_progress)
                
            threading.Thread(target=process, daemon=True).start()

    def populate_tree(self):
        import time
        t0 = time.perf_counter()
        print(f"[LOG] Starting tree population: {len(self.groups)} groups")
        
        # Update status bar for tree population
        total_duplicates = sum(len(group) - 1 for group in self.groups)
        self.status_var.set(f"Building tree view for {len(self.groups)} images with duplicates...")
        
        self.tree.delete(*self.tree.get_children())
        
        if not self.groups:
            no_duplicates_id = self.tree.insert("", "end", text="✅ No duplicates found", tags=("no_duplicates",))
            return
        
        for i, group in enumerate(self.groups, 1):
            # Use first filename as the group name with duplicate count
            first_filename = os.path.basename(group[0])
            duplicate_count = len(group) - 1  # Number of duplicates (excluding the original)
            group_text = f"📂 {first_filename} ({duplicate_count} duplicate{'s' if duplicate_count != 1 else ''})"
            group_node = self.tree.insert("", "end", text=group_text, open=False)
            
            if len(group) > 100:
                print(f"[LOG] Group {i} is large ({len(group)} images), inserting in chunks...")
                chunk_size = 100
                for start in range(0, len(group), chunk_size):
                    end = min(start + chunk_size, len(group))
                    for img_path in group[start:end]:
                        filename = os.path.basename(img_path)
                        self.tree.insert(group_node, "end", text=f"🖼️ {filename}", values=(img_path,))
            else:
                for img_path in group:
                    filename = os.path.basename(img_path)
                    self.tree.insert(group_node, "end", text=f"🖼️ {filename}", values=(img_path,))
        
        print(f"[LOG] Finished tree population in {time.perf_counter()-t0:.2f}s")
        
        # Update status bar when tree population is complete
        if len(self.groups) > 0:
            total_images = sum(len(group) for group in self.groups)
            total_duplicates = sum(len(group) - 1 for group in self.groups)
            self.status_var.set(f"Ready - {len(self.groups)} images have duplicates ({total_duplicates} total duplicates)")
        else:
            self.status_var.set("No duplicates found - all images are unique")
        
        # Initialize zoom controls
        self.update_zoom_controls()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            # Update clean button count for empty selection
            self.update_clean_button_count()
            return
        
        # Clear previous images and selection tracking
        for widget in self.img_panel.winfo_children():
            widget.destroy()
        self.selected_check_vars.clear()  # Clear checkbox tracking
        
        # Handle both single and multiple selection with unified method
        self.display_groups(selected)
        
        # Update clean button count
        self.update_clean_button_count()
        
        # Update scroll region
        self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
    
    def display_groups(self, selected_items):
        """Unified method to display images from single or multiple selected groups"""
        total_images = 0
        current_row = 0
        is_single_group = len(selected_items) == 1
        
        # Choose appropriate thumbnail size and layout
        thumb_size = self.thumb_size if is_single_group else self.multi_thumb_size
        
        for item_id in selected_items:
            item = self.tree.item(item_id)
            
            # Skip if not a group node or if it's a placeholder
            if ('values' in item and item['values']) or "No duplicates found" in item['text'] or "Select a folder" in item['text']:
                continue
            
            # Get group name
            group_name = item['text']
            
            # Create group header (only for multiple groups or single group with multiple images)
            children = self.tree.get_children(item_id)
            show_header = not is_single_group or len(children) > 1
            
            if show_header:
                group_header = tk.Frame(self.img_panel, bg=self.colors['bg_secondary'], height=40)
                group_header.grid(row=current_row, column=0, columnspan=10, sticky='ew', padx=5, pady=(5, 0))
                group_header.grid_propagate(False)
                
                header_label = tk.Label(group_header, 
                                       text=f"📂 {group_name}", 
                                       font=("Segoe UI", 12, "bold"),
                                       bg=self.colors['bg_secondary'],
                                       fg=self.colors['text_primary'])
                header_label.pack(side=tk.LEFT, padx=10, pady=8)
                
                current_row += 1
            
            # Get images for this group
            children = self.tree.get_children(item_id)
            group_images = []
            
            for child in children:
                child_item = self.tree.item(child)
                if 'values' in child_item and child_item['values']:
                    img_path = child_item['values'][0]
                    try:
                        img = Image.open(img_path)
                        img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        group_images.append((img_tk, img_path))
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                        continue
            
            # Display images with appropriate layout
            if group_images:
                if is_single_group:
                    # Grid layout for single group (better space utilization)
                    self.display_images_in_grid(group_images, current_row)
                else:
                    # Row layout for multiple groups
                    self.display_images_in_row(group_images, current_row)

                
                total_images += len(group_images)
                current_row += 1
        
        # Update result label and status
        if is_single_group:
            self.lbl_result.config(text=f"Viewing group - {total_images} images", 
                                 fg=self.colors['text_primary'])
            self.status_var.set(f"Viewing duplicate group with {total_images} images")
        else:
            self.lbl_result.config(text=f"Viewing {len(selected_items)} groups - {total_images} total images", 
                                 fg=self.colors['text_primary'])
            self.status_var.set(f"Viewing {len(selected_items)} groups with {total_images} images")
    
    def display_images_in_grid(self, group_images, start_row):
        """Display images in a grid layout (for single group selection)"""
        canvas_width = self.img_canvas.winfo_width() or 800
        cols = max(1, (canvas_width - 40) // 200)
        
        for idx, (img_tk, img_path) in enumerate(group_images):
            row = start_row + (idx // cols)
            col = idx % cols
            
            self.create_image_card(img_tk, img_path, row, col, is_grid=True)
    
    def display_images_in_row(self, group_images, row):
        """Display images in a single row layout (for multiple group selection)"""
        images_frame = tk.Frame(self.img_panel, bg=self.colors['bg_primary'])
        images_frame.grid(row=row, column=0, columnspan=10, sticky='ew', padx=5, pady=(0, 10))
        
        for col, (img_tk, img_path) in enumerate(group_images):
            self.create_image_card(img_tk, img_path, 0, col, parent=images_frame, is_grid=False)
    
    def create_image_card(self, img_tk, img_path, row, col, parent=None, is_grid=True):
        """Create a unified image card with canvas, checkbox, and similarity score"""
        if parent is None:
            parent = self.img_panel
            
        # Create image card
        card = tk.Frame(parent, 
                       bg=self.colors['bg_card'], 
                       bd=0,
                       highlightbackground=self.colors['bg_secondary'],
                       highlightthickness=1,
                       relief=tk.SOLID)
        
        if is_grid:
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        else:
            card.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Image container
        padding = 8 if is_grid else 5
        img_container = tk.Frame(card, bg=self.colors['bg_card'])
        img_container.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
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
        setattr(img_canvas, 'img_path', img_path)
        
        # Info section for checkbox and similarity score
        info_frame = tk.Frame(img_container, bg=self.colors['bg_card'])
        info_frame.pack(fill=tk.X, pady=(5 if is_grid else 3, 0))
        
        # Checkbox and filename
        var = tk.BooleanVar()
        filename = os.path.basename(img_path)
        max_length = 18 if is_grid else 12
        truncate_length = 15 if is_grid else 9
        
        if len(filename) > max_length:
            display_filename = filename[:truncate_length] + "..."
        else:
            display_filename = filename
        
        font_size = 9 if is_grid else 8
        chk = tk.Checkbutton(info_frame,
                           text=display_filename,
                           variable=var,
                           command=lambda v=var, p=img_path: self.on_image_check(v, p),
                           font=("Segoe UI", font_size, "bold"),
                           bg=self.colors['bg_card'],
                           fg=self.colors['text_primary'],
                           activebackground=self.colors['bg_card'],
                           selectcolor=self.colors['accent'],
                           bd=0, highlightthickness=0,
                           anchor="w")
        chk.pack(fill=tk.X, pady=(0, 2 if is_grid else 1))
        
        # Similarity score with color coding
        if img_path in self.similarity_scores:
            similarity = self.similarity_scores[img_path]
            sim_text = f"Similarity: {similarity:.0%}" if is_grid else f"{similarity:.0%}"
            
            # Color code based on similarity
            if similarity >= 0.98:
                sim_color = self.colors['success']
            elif similarity >= 0.96:
                sim_color = self.colors['accent']
            elif similarity >= 0.95:
                sim_color = self.colors['warning']
            else:
                sim_color = self.colors['danger']
            
            sim_font_size = 8 if is_grid else 7
            sim_label = tk.Label(info_frame,
                               text=sim_text,
                               font=("Segoe UI", sim_font_size),
                               bg=self.colors['bg_card'],
                               fg=sim_color,
                               anchor="w")
            sim_label.pack(fill=tk.X)
            
            # Add tooltip for similarity score
            tooltip_text = self.get_similarity_tooltip(similarity)
            ToolTip(sim_label, tooltip_text)
        
        # Store checkbox and canvas references
        self.selected_check_vars.append((var, img_path, img_canvas))
        
        # Hover effects
        def on_enter(e, card=card):
            card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
        
        def on_leave(e, card=card):
            card.configure(highlightbackground=self.colors['bg_secondary'], highlightthickness=1)
        
        for widget in [card, img_canvas, chk]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def zoom_in(self):
        """Increase thumbnail size for better image viewing"""
        current_width, current_height = self.thumb_size
        new_width = min(int(current_width * 1.1), self.max_thumb_size[0])
        new_height = min(int(current_height * 1.1), self.max_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            # Also scale the multi-group thumbnail size proportionally
            self.multi_thumb_size = (int(new_width * 0.83), int(new_height * 0.89))
            self.refresh_current_view()
            self.update_zoom_controls()
            
    def zoom_out(self):
        """Decrease thumbnail size for more images in view"""
        current_width, current_height = self.thumb_size
        new_width = max(int(current_width * 0.9), self.min_thumb_size[0])
        new_height = max(int(current_height * 0.9), self.min_thumb_size[1])
        if (new_width, new_height) != self.thumb_size:
            self.thumb_size = (new_width, new_height)
            # Also scale the multi-group thumbnail size proportionally
            self.multi_thumb_size = (int(new_width * 0.83), int(new_height * 0.89))
            self.refresh_current_view()
            self.update_zoom_controls()
            
    def update_zoom_controls(self):
        """Update zoom button states and percentage label"""
        can_zoom_in = self.thumb_size[0] < self.max_thumb_size[0]
        can_zoom_out = self.thumb_size[0] > self.min_thumb_size[0]
        self.zoom_in_btn.config(state=tk.NORMAL if can_zoom_in else tk.DISABLED)
        self.zoom_out_btn.config(state=tk.NORMAL if can_zoom_out else tk.DISABLED)
        
        # Calculate and display zoom percentage
        base_width = 180  # Reference width (default thumb_size)
        zoom_level = int((self.thumb_size[0] / base_width) * 100)
        self.zoom_label.config(text=f"{zoom_level}%")
    
    def refresh_current_view(self):
        """Refresh the current image view after zoom change"""
        selected = self.tree.selection()
        if selected:
            # Save current checkbox states before refresh
            checkbox_states = {}
            for item in self.selected_check_vars:
                if len(item) >= 2:
                    var, img_path = item[0], item[1]
                    checkbox_states[img_path] = var.get()
            
            # Clear current display
            for widget in self.img_panel.winfo_children():
                widget.destroy()
            
            # Clear old canvas references
            self.selected_check_vars.clear()
            
            # Redisplay with new thumbnail sizes using unified method
            self.display_groups(selected)
            
            # Restore checkbox states and apply cross overlays after UI update
            self.root.after(50, lambda: self.restore_checkbox_states(checkbox_states))
                
            # Update scroll region
            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
    
    def select_all_groups(self):
        """Select all images via checkboxes, or all groups if no images displayed"""
        # If there are image checkboxes visible, toggle them
        if self.selected_check_vars:
            self.toggle_select_all_images()
        else:
            # Otherwise, select all tree items
            if not self.tree:
                return
                
            # Clear current selection
            self.tree.selection_remove(self.tree.selection())
            
            # Select all items in the tree
            all_items = self.tree.get_children()
            for item in all_items:
                self.tree.selection_add(item)
                
            # Update clean button count
            self.update_clean_button_count()
    
    def clean_selected_images(self):
        """Move selected duplicate images to trash"""
        # Check if we have checkbox selections
        if self.selected_check_vars:
            # Use checkbox selections
            images_to_clean = []
            for item in self.selected_check_vars:
                if len(item) >= 2:
                    var, img_path = item[0], item[1]
                if var.get() and os.path.exists(img_path):
                    images_to_clean.append(img_path)
            
            if not images_to_clean:
                messagebox.showinfo("No Selection", "Please select images using checkboxes to clean.")
                return
            
            # Confirm cleaning action
            result = messagebox.askyesno(
                "Confirm Clean", 
                f"Move {len(images_to_clean)} selected images to trash?\n\nThis action cannot be undone.",
                icon='warning'
            )
            
            if result:
                self.move_images_to_trash(images_to_clean)
                # Refresh the display
                self.refresh_after_clean()
        else:
            # Fallback to tree selection method
            selected_items = self.tree.selection() if self.tree else []
            if not selected_items:
                messagebox.showinfo("No Selection", "Please select duplicate groups to clean.")
                return
            
            # Count images to be cleaned from selected groups
            images_to_clean = []
            groups_processed = 0
            
            for item in selected_items:
                # Get children (individual images) of selected group
                children = self.tree.get_children(item)
                if len(children) > 1:  # Only clean if there are duplicates
                    groups_processed += 1
                    # Keep the first image, clean the rest
                    for i, child in enumerate(children[1:], 1):
                        child_item = self.tree.item(child)
                        if 'values' in child_item and child_item['values']:
                            img_path = child_item['values'][0]
                            if img_path and os.path.exists(img_path):
                                images_to_clean.append(img_path)
            
            if not images_to_clean:
                messagebox.showinfo("Nothing to Clean", "No duplicate images found in selection.")
                return
            
            # Confirm cleaning action
            result = messagebox.askyesno(
                "Confirm Clean", 
                f"Move {len(images_to_clean)} duplicate images from {groups_processed} groups to trash?\n\nThis action cannot be undone.",
                icon='warning'
            )
            
            if result:
                self.move_images_to_trash(images_to_clean)
                # Refresh the display
                self.refresh_after_clean()
    
    def move_images_to_trash(self, image_paths):
        """Move images to system trash"""
        try:
            import send2trash
            moved_count = 0
            
            for img_path in image_paths:
                try:
                    if os.path.exists(img_path):
                        send2trash.send2trash(img_path)
                        moved_count += 1
                except Exception as e:
                    print(f"Error moving {img_path} to trash: {e}")
            
            messagebox.showinfo("Clean Complete", f"Successfully moved {moved_count} images to trash.")
            
        except ImportError:
            # Fallback - create a PhotoSift trash folder
            self.create_photosift_trash(image_paths)
    
    def create_photosift_trash(self, image_paths):
        """Create PhotoSift trash folder and move images there"""
        try:
            # Create trash folder in PhotoSift directory
            trash_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "PhotoSift_Trash")
            os.makedirs(trash_dir, exist_ok=True)
            
            moved_count = 0
            for img_path in image_paths:
                try:
                    if os.path.exists(img_path):
                        filename = os.path.basename(img_path)
                        trash_path = os.path.join(trash_dir, filename)
                        
                        # Handle duplicate names in trash
                        counter = 1
                        base_name, ext = os.path.splitext(filename)
                        while os.path.exists(trash_path):
                            new_name = f"{base_name}_{counter}{ext}"
                            trash_path = os.path.join(trash_dir, new_name)
                            counter += 1
                        
                        import shutil
                        shutil.move(img_path, trash_path)
                        moved_count += 1
                except Exception as e:
                    print(f"Error moving {img_path} to PhotoSift trash: {e}")
            
            messagebox.showinfo("Clean Complete", 
                              f"Successfully moved {moved_count} images to PhotoSift_Trash folder.\n"
                              f"Location: {trash_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create trash folder: {e}")
    
    def open_trash_folder(self):
        """Open the PhotoSift trash folder"""
        trash_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "PhotoSift_Trash")
        
        if os.path.exists(trash_dir):
            # Open folder in Windows Explorer
            os.startfile(trash_dir)
        else:
            messagebox.showinfo("Trash Empty", "No PhotoSift trash folder found. No items have been cleaned yet.")
    
    def update_clean_button_count(self):
        """Update the clean button with the count of selected items"""
        if not hasattr(self, 'clean_btn_var'):
            return
            
        # Priority: Use checkbox selections if available, otherwise use tree selection
        if self.selected_check_vars:
            # Count selected checkboxes
            selected_count = sum(1 for var, _ in self.selected_check_vars if var.get())
        elif self.tree:
            # Fall back to tree selection count
            selected_count = len(self.tree.selection())
        else:
            selected_count = 0
            
        self.clean_btn_var.set(f"Clean ({selected_count})")
    
    def on_image_check(self, var, img_path):
        """Handle individual image checkbox selection"""
        # Skip update if we're doing bulk selection to prevent performance issues
        if getattr(self, '_updating_bulk_selection', False):
            return
            
        # Update cross overlay on image
        self.update_cross_overlay(var, img_path)
            
        # Update clean button count based on selected images
        selected_count = sum(1 for item in self.selected_check_vars 
                           if len(item) >= 2 and item[0].get())
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")
    
    def count_selected_images(self):
        """Count how many images are currently selected via checkboxes"""
        return sum(1 for item in self.selected_check_vars 
                  if len(item) >= 2 and item[0].get())
    
    def toggle_select_all_images(self):
        """Toggle selection of all visible images"""
        if not self.selected_check_vars:
            return
            
        # Check current state of first checkbox to determine action
        first_var = self.selected_check_vars[0][0]
        new_state = not first_var.get()
        
        # Temporarily disable callback updates to prevent performance issues
        self._updating_bulk_selection = True
        
        try:
            # Apply to all checkboxes
            for item in self.selected_check_vars:
                if len(item) >= 2:
                    var, img_path = item[0], item[1]
                    var.set(new_state)
        finally:
            # Re-enable callback updates
            self._updating_bulk_selection = False
        
        # Update all cross overlays
        for item in self.selected_check_vars:
            if len(item) >= 2:
                var, img_path = item[0], item[1]
                self.update_cross_overlay(var, img_path)
        
        # Update clean button once at the end
        selected_count = self.count_selected_images()
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")
    
    def refresh_after_clean(self):
        """Refresh the duplicate detection after cleaning images"""
        messagebox.showinfo("Clean Complete", 
                          "Images moved to trash. Please select the folder again to refresh duplicate detection.")
    
    def restore_checkbox_states(self, checkbox_states):
        """Restore checkbox states and cross overlays after refresh"""
        # Temporarily disable bulk selection flag to allow individual updates
        self._updating_bulk_selection = True
        
        try:
            # Restore checkbox states
            for item in self.selected_check_vars:
                if len(item) >= 2:
                    var, img_path = item[0], item[1]
                    if img_path in checkbox_states:
                        var.set(checkbox_states[img_path])
        finally:
            self._updating_bulk_selection = False
        
        # Apply cross overlays for checked items
        for item in self.selected_check_vars:
            if len(item) >= 2:
                var, img_path = item[0], item[1]
                if img_path in checkbox_states and checkbox_states[img_path]:
                    self.update_cross_overlay(var, img_path)
        
        # Update clean button count
        selected_count = self.count_selected_images()
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")

    def update_cross_overlay(self, var, img_path):
        """Add or remove cross overlay on image based on checkbox state"""
        # Find the canvas for this image path
        canvas = None
        for item in self.selected_check_vars:
            if len(item) >= 3 and item[1] == img_path:
                canvas = item[2]
                break
        
        if not canvas:
            return
            
        # Remove existing cross if any
        canvas.delete("cross_overlay")
        
        # If checkbox is checked, draw cross overlay
        if var.get():
            # Try to get actual canvas dimensions
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            # Fallback to configured size if not yet mapped
            if width <= 1 or height <= 1:
                width = canvas.winfo_reqwidth()
                height = canvas.winfo_reqheight()
                
            # Final fallback to image size from canvas config
            if width <= 1 or height <= 1:
                width = canvas['width'] if 'width' in canvas.keys() else 100
                height = canvas['height'] if 'height' in canvas.keys() else 100
            
            # Draw red cross lines
            line_width = max(2, min(width, height) // 30)
            
            # Diagonal cross from top-left to bottom-right
            canvas.create_line(0, 0, width, height, 
                             fill="#ff0000", width=line_width, tags="cross_overlay")
            
            # Diagonal cross from top-right to bottom-left  
            canvas.create_line(width, 0, 0, height,
                             fill="#ff0000", width=line_width, tags="cross_overlay")

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageIdentifierApp(root)
    root.mainloop()
