import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
from DuplicateImageIdentifier import group_similar_images_clip, IMG_EXT

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
        
        # App title with modern styling
        title_frame = tk.Frame(header, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(title_frame, 
                 text="PhotoSift", 
                 font=("Segoe UI", 24, "bold"),
                 bg=self.colors['bg_primary'], 
                 fg=self.colors['text_primary']).pack(anchor="w")
        
        tk.Label(title_frame, 
                 text="Duplicate Image Identifier", 
                 font=("Segoe UI", 12),
                 bg=self.colors['bg_primary'], 
                 fg=self.colors['text_secondary']).pack(anchor="w")

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
        groups_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 0))
        
        tk.Label(groups_section, 
                text="📊 Duplicate Groups", 
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
                               show="tree")
        
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
                    
                    self.groups = group_similar_images_clip(folder=folder, embeddings=embeddings, files=files, 
                                                          progress_callback=duplicate_progress_callback)
                    
                    # Update final status
                    final_status = f"Complete! Found {len(self.groups)} duplicate groups"
                    final_detail = f"Processed {total} images successfully"
                    self.update_progress(total, total, final_status, final_detail)
                    
                    # Update status bar with final result
                    final_status_text = f"Done! Found {len(self.groups)} duplicate groups from {total} images (100%)"
                    self.root.after(0, self.status_var.set, final_status_text)
                    self.root.after(0, self.status_bar.config, {"bg": "#33cc33", "fg": "white"})
                    
                    # Update main UI
                    self.lbl_result.config(text=f"Found {len(self.groups)} duplicate groups", 
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
        self.status_var.set(f"Building tree view for {len(self.groups)} duplicate groups...")
        
        self.tree.delete(*self.tree.get_children())
        
        if not self.groups:
            no_duplicates_id = self.tree.insert("", "end", text="✅ No duplicates found", tags=("no_duplicates",))
            return
        
        for i, group in enumerate(self.groups, 1):
            group_text = f"📂 Group {i} ({len(group)} images)"
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
            self.status_var.set(f"Ready - {len(self.groups)} duplicate groups with {total_images} images")
        else:
            self.status_var.set("No duplicates found - all images are unique")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        
        # Clear previous images
        for widget in self.img_panel.winfo_children():
            widget.destroy()
        
        # If group node (no 'values'), show all images in group
        if not ('values' in item and item['values']):
            if "No duplicates found" in item['text'] or "Select a folder" in item['text']:
                return
                
            # Find group images
            children = self.tree.get_children(selected[0])
            images = []
            
            for child in children:
                child_item = self.tree.item(child)
                if 'values' in child_item and child_item['values']:
                    img_path = child_item['values'][0]
                    try:
                        img = Image.open(img_path)
                        img.thumbnail((180, 135), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img)
                        images.append((img_tk, img_path))
                    except Exception as e:
                        print(f"Error loading image {img_path}: {e}")
                        continue
            
            # Calculate grid layout
            if images:
                canvas_width = self.img_canvas.winfo_width() or 800
                cols = max(1, (canvas_width - 40) // 200)  # 200px per thumbnail + spacing
                
                # Display thumbnails in modern cards
                for idx, (img_tk, img_path) in enumerate(images):
                    row = idx // cols
                    col = idx % cols
                    
                    # Modern card frame
                    card = tk.Frame(self.img_panel, 
                                   bg=self.colors['bg_card'], 
                                   bd=0,
                                   highlightbackground=self.colors['bg_secondary'],
                                   highlightthickness=1,
                                   relief=tk.SOLID)
                    card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                    
                    # Image container with padding
                    img_container = tk.Frame(card, bg=self.colors['bg_card'])
                    img_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
                    
                    # Image label
                    lbl_img = tk.Label(img_container, image=img_tk, bg=self.colors['bg_card'], bd=0)
                    lbl_img.image = img_tk  # Keep reference
                    lbl_img.pack()
                    
                    # Filename label
                    filename = os.path.basename(img_path)
                    if len(filename) > 20:
                        filename = filename[:17] + "..."
                    
                    lbl_name = tk.Label(img_container, 
                                       text=filename, 
                                       font=("Segoe UI", 10),
                                       bg=self.colors['bg_card'],
                                       fg=self.colors['text_primary'],
                                       wraplength=180)
                    lbl_name.pack(pady=(5, 0))
                    
                    # Hover effects
                    def on_enter(e, card=card):
                        card.configure(highlightbackground=self.colors['accent'], highlightthickness=2)
                    
                    def on_leave(e, card=card):
                        card.configure(highlightbackground=self.colors['bg_secondary'], highlightthickness=1)
                    
                    card.bind("<Enter>", on_enter)
                    card.bind("<Leave>", on_leave)
                    lbl_img.bind("<Enter>", on_enter)
                    lbl_img.bind("<Leave>", on_leave)
                    lbl_name.bind("<Enter>", on_enter)
                    lbl_name.bind("<Leave>", on_leave)
                
                self.lbl_result.config(text=f"Group: {item['text']} - {len(images)} images", 
                                     fg=self.colors['text_primary'])
                
                # Update status bar when viewing a group
                self.status_var.set(f"Viewing duplicate group with {len(images)} similar images")
                
        # If leaf node, show single image enlarged
        elif 'values' in item and item['values']:
            path = item['values'][0]
            try:
                img = Image.open(path)
                img.thumbnail((600, 450), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                
                # Center the single image
                single_frame = tk.Frame(self.img_panel, bg=self.colors['bg_primary'])
                single_frame.pack(expand=True, fill=tk.BOTH)
                
                lbl = tk.Label(single_frame, image=img_tk, bg=self.colors['bg_primary'])
                lbl.image = img_tk
                lbl.pack(expand=True)
                
                self.lbl_result.config(text=os.path.basename(path), fg=self.colors['text_primary'])
                
                # Update status bar when viewing a single image
                self.status_var.set(f"Viewing: {os.path.basename(path)}")
            except Exception as e:
                self.lbl_result.config(text=f"Error loading image: {e}", fg=self.colors['danger'])
        
        # Update scroll region
        self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageIdentifierApp(root)
    root.mainloop()
