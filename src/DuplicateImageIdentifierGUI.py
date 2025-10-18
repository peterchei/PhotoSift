import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
import time
from DuplicateImageIdentifier import group_similar_images_clip, IMG_EXT
from CommonUI import (ToolTip, ModernColors, ProgressWindow, ModernStyling, 
                     StatusBar, ZoomControls, ModernButton, ImageUtils, TrashManager)
from CommonUI import get_trash_icon_tk

class DuplicateImageIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoSift - Duplicate Image Identifier")
        self.root.state('zoomed')  # Start maximized
        
        # Use centralized color scheme
        self.colors = ModernColors.get_color_scheme()
        
        self.folder = None
        self.groups = []
        self.embeddings = {}  # Store embeddings for re-grouping with different thresholds
        self.files = []  # Store file list for re-grouping
        
        # Selection and confidence tracking
        self.selected_check_vars = []  # List of (checkbox_var, image_path, img_canvas) tuples
        self.similarity_scores = {}  # path -> similarity score for duplicates
        self._updating_bulk_selection = False  # Flag to prevent callback loops during bulk operations
        self._cleaning_in_progress = False  # Flag to prevent UI updates during cleaning
        self._refresh_in_progress = False  # Flag to prevent recursive tree selection during refresh
        
        # Thumbnail size configuration for zoom functionality
        self.thumb_size = (180, 135)  # Default size for single group view
        self.multi_thumb_size = (150, 120)  # Default size for multi-group view
        self.min_thumb_size = (80, 60)  # Minimum size
        self.max_thumb_size = (300, 225)  # Maximum size
        
        # Paging variables
        self.page_size = 10  # groups per page (changed from images to groups)
        self.current_page = 0
        self.current_display_groups = []  # Store current groups being displayed for paging (changed from images)
        
        # Image caching system for performance
        self.image_cache = {}  # cache_key -> ImageTk.PhotoImage
        self.cache_access_order = []  # For LRU cache management
        self.max_cache_size = 300  # Maximum number of cached images
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        
        # Initialize progress window
        self.progress_window = ProgressWindow(self.root, "Processing Images - Duplicate Detection")
        
        self.setup_ui()
        ModernStyling.apply_modern_styling(self.colors)
        
        # Create status bar using common component
        self.status_bar = StatusBar(self.root, self.colors, "Ready - Select a folder to find duplicates")

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
        
        # Create trash manager using common component
        self.trash_manager = TrashManager(
            header_buttons, self.colors, lambda: self.folder, IMG_EXT, button_style="emoji")
        self.trash_manager.pack(side=tk.RIGHT, padx=(10, 0))

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
        
        # Modern select folder button using common component
        self.select_btn = ModernButton.create_primary_button(
            folder_section, "Select Folder", self.select_folder, self.colors)
        self.select_btn.pack(fill=tk.X)
        
        # Folder path display
        self.lbl_folder = tk.Label(folder_section, 
                                  text="No folder selected", 
                                  font=("Segoe UI", 10),
                                  bg=self.colors['bg_secondary'], 
                                  fg=self.colors['text_secondary'],
                                  wraplength=240,
                                  justify=tk.LEFT)
        self.lbl_folder.pack(anchor="w", pady=(5, 0))
        
        # Image count display
        self.lbl_image_count = tk.Label(folder_section, 
                                        text="", 
                                        font=("Segoe UI", 9),
                                        bg=self.colors['bg_secondary'], 
                                        fg=self.colors['text_secondary'])
        self.lbl_image_count.pack(anchor="w", pady=(5, 0))
        
        # Similarity Threshold control
        threshold_section = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        threshold_section.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        tk.Label(threshold_section, text="Similarity Threshold", 
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor="w")
        
        self.threshold_var = tk.DoubleVar(value=0.95)
        self.threshold_slider = ttk.Scale(threshold_section, from_=0.80, to=0.99, 
                                          orient=tk.HORIZONTAL, variable=self.threshold_var,
                                          command=self.update_threshold_label)
        self.threshold_slider.pack(fill=tk.X, pady=(5, 0))
        ToolTip(self.threshold_slider, 
                "Adjust similarity threshold for grouping duplicates.\n"
                "Higher values (0.95-0.99): Only very similar images\n"
                "Lower values (0.80-0.90): Include more loosely similar images")
        
        self.lbl_threshold = tk.Label(threshold_section, text="Current: 95%",
                                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                      font=("Segoe UI", 10))
        self.lbl_threshold.pack(anchor="w")
        
        # Threshold quality guide
        threshold_guide_frame = tk.Frame(threshold_section, bg=self.colors['bg_secondary'])
        threshold_guide_frame.pack(fill=tk.X, pady=(5, 0))
        
        guide_text = "• 98-99%: Identical images\n• 95-97%: Near duplicates\n• 90-94%: Similar images\n• 80-89%: Loosely related"
        tk.Label(threshold_guide_frame, text=guide_text,
                font=("Segoe UI", 8),
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                justify=tk.LEFT).pack(anchor="w")
        
        # Scan button
        self.scan_btn = ModernButton.create_primary_button(
            threshold_section, "Start Scan", self.start_scan, self.colors)
        self.scan_btn.pack(fill=tk.X, pady=(15, 0))
        self.scan_btn.config(state=tk.DISABLED)  # Disabled until folder is selected
        ToolTip(self.scan_btn, "Begin scanning for duplicate images in the selected folder")
        
        # Re-group button (shown only after initial scan)
        self.regroup_btn = ModernButton.create_secondary_button(
            threshold_section, "Re-group with New Threshold", self.regroup_duplicates, self.colors)
        self.regroup_btn.pack(fill=tk.X, pady=(10, 0))
        self.regroup_btn.pack_forget()  # Hide initially until first scan completes
        ToolTip(self.regroup_btn, 
                "Re-analyze duplicates with the current threshold.\n"
                "This is fast since images don't need to be re-processed.")
        
        # Groups section
        groups_section = tk.Frame(sidebar, bg=self.colors['bg_secondary'])
        groups_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 0))
        
        self.duplications_label = tk.Label(groups_section, 
                text="Duplications", 
                font=("Segoe UI", 14, "bold"),
                bg=self.colors['bg_secondary'], 
                fg=self.colors['text_primary'])
        self.duplications_label.pack(anchor="w", pady=(0, 10))
        
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
        self.tree.bind("<Control-a>", self.handle_ctrl_a)
        
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
        
        # Use common zoom controls
        self.zoom_controls = ZoomControls(nav_bar, self.colors, self.zoom_in, self.zoom_out)
        self.zoom_controls.pack(side=tk.LEFT, fill=tk.Y)
        
        # Action buttons (right side of nav bar)
        action_frame = tk.Frame(nav_bar, bg=self.colors['bg_primary'])
        action_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons using ModernButton factory
        # Select All button with variable text that updates based on state
        self.select_all_btn_var = tk.StringVar()
        self.select_all_btn_var.set("Select All")
        self.select_all_btn = ModernButton.create_primary_button(
            action_frame, "", self.select_all_groups, self.colors,
            textvariable=self.select_all_btn_var)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add tooltip to Select All button
        ToolTip(self.select_all_btn, 
                "Toggle selection of duplicates in displayed images.\n"
                "Keeps first image in each group unchecked (as original).\n"
                "Click again to unselect all duplicates.")
        
        # Clean button with variable text
        self.clean_btn_var = tk.StringVar()
        self.clean_btn_var.set("Clean (0)")
        self.clean_btn = ModernButton.create_danger_button(
            action_frame, "", self.clean_selected_images, self.colors, 
            textvariable=self.clean_btn_var)
        self.clean_btn.pack(side=tk.LEFT)
        
        # Add tooltip to Clean button
        ToolTip(self.clean_btn, 
                "Move selected images to Trash folder.\n"
                "Check images you want to remove, then click Clean.\n"
                "Images will be moved to a local Trash folder for safety.")
        
        # Modern pagination controls
        self.page_frame = tk.Frame(main_area, bg=self.colors['bg_primary'], height=50)
        self.page_frame.pack(fill=tk.X, pady=(0, 20))
        self.page_frame.pack_propagate(False)
        
        # Center container for navigation
        nav_center = tk.Frame(self.page_frame, bg=self.colors['bg_primary'])
        nav_center.pack(expand=True)
        
        # Modern navigation buttons
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
        
        # Image display area with scrolling
        self.create_image_display_area(main_area)

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
        """Show progress window using common component"""
        self.progress_window.show(total, "Initializing Duplicate Detection...")

    def update_progress(self, current, total, status_text, detail_text=""):
        """Update progress window using common component"""
        self.progress_window.update(current, total, status_text, detail_text)

    def close_progress(self):
        """Close progress window using common component"""
        self.progress_window.close()
    
    def update_threshold_label(self, value):
        """Update threshold label when slider moves"""
        percentage = int(float(value) * 100)
        self.lbl_threshold.config(text=f"Current: {percentage}%")
    
    def regroup_duplicates(self):
        """Re-group duplicates using the current threshold without re-extracting embeddings"""
        if not self.embeddings or not self.files:
            messagebox.showinfo("No Data", "Please scan a folder first before re-grouping.")
            return
        
        if not self.folder:
            messagebox.showinfo("No Folder", "Please select a folder first.")
            return
        
        threshold = self.threshold_var.get()
        threshold_percent = int(threshold * 100)
        total = len(self.files)
        
        # Show progress window
        self.show_progress_window(total)
        self.update_progress(0, total, f"Re-grouping with {threshold_percent}% threshold...", 
                           "Using cached embeddings for fast re-grouping...")
        
        # Process in thread
        import threading
        def process():
            try:
                from DuplicateImageIdentifier import group_similar_images_clip
                
                # Update status bar
                self.root.after(0, self.status_bar.set_text, f"Re-grouping duplicates at {threshold_percent}% similarity...")
                
                # Define progress callback for duplicate detection
                def duplicate_progress_callback(current, total_imgs, status_text, detail_text):
                    self.root.after(0, self.update_progress, current, total_imgs, status_text, detail_text)
                    percent = int((current / total_imgs) * 100) if total_imgs > 0 else 100
                    status_bar_text = f"Re-grouping: {current}/{total_imgs} ({percent}%)"
                    self.root.after(0, self.status_bar.set_text, status_bar_text)
                
                # Re-group using cached embeddings with new threshold
                result = group_similar_images_clip(folder=self.folder, threshold=threshold, 
                                                 embeddings=self.embeddings, files=self.files, 
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
                final_status = f"Re-grouping Complete! Found {len(self.groups)} images with duplicates (≥{threshold_percent}% similarity)"
                final_detail = f"Analyzed {total} images - {total_duplicates} total duplicates found"
                self.update_progress(total, total, final_status, final_detail)
                
                # Update status bar with final result
                final_status_text = f"Done! {len(self.groups)} images have duplicates ({total_duplicates} total) at {threshold_percent}% similarity threshold"
                self.root.after(0, self.status_bar.set_text, final_status_text)
                self.root.after(0, self.status_bar.set_color, "#33cc33", "white")
                
                # Update main UI
                self.populate_tree()
                
                # Automatically select all groups in tree view to display results
                self.root.after(100, self.auto_select_all_groups)
                
                # Close progress window after a short delay
                self.root.after(2000, self.close_progress)
                
            except Exception as e:
                # Handle errors gracefully
                error_msg = f"Error during re-grouping: {str(e)}"
                print(f"[ERROR] {error_msg}")
                
                self.update_progress(0, total, "Re-grouping Failed", error_msg)
                
                # Update status bar with error
                self.root.after(0, self.status_bar.set_text, f"Re-grouping failed: {str(e)}")
                self.root.after(0, self.status_bar.set_color, "#cc3333", "white")
                
                # Close progress window after error
                self.root.after(3000, self.close_progress)
        
        threading.Thread(target=process, daemon=True).start()

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

    def get_cached_thumbnail(self, img_path, thumb_size):
        """Get cached thumbnail or create and cache new one with LRU management"""
        # Create unique cache key based on path and size
        cache_key = f"{img_path}_{thumb_size[0]}x{thumb_size[1]}"
        
        # Check if image is in cache
        if cache_key in self.image_cache:
            self.cache_stats['hits'] += 1
            # Move to end for LRU management
            self.cache_access_order.remove(cache_key)
            self.cache_access_order.append(cache_key)
            return self.image_cache[cache_key]
        
        # Cache miss - load and process image
        self.cache_stats['misses'] += 1
        
        try:
            # Load and resize image
            img = Image.open(img_path)
            img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Manage cache size with LRU eviction
            if len(self.image_cache) >= self.max_cache_size:
                # Remove oldest entries (LRU)
                evict_count = max(1, self.max_cache_size // 10)  # Remove 10% when full
                for _ in range(evict_count):
                    if self.cache_access_order:
                        oldest_key = self.cache_access_order.pop(0)
                        if oldest_key in self.image_cache:
                            del self.image_cache[oldest_key]
                            self.cache_stats['evictions'] += 1
            
            # Cache the result
            self.image_cache[cache_key] = img_tk
            self.cache_access_order.append(cache_key)
            return img_tk
            
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            return None
    
    def clear_image_cache(self):
        """Clear the image cache and reset statistics"""
        self.image_cache.clear()
        self.cache_access_order.clear()
        print(f"Cache cleared. Stats - Hits: {self.cache_stats['hits']}, Misses: {self.cache_stats['misses']}, Evictions: {self.cache_stats['evictions']}")
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def print_cache_stats(self):
        """Print current cache statistics for performance monitoring"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests > 0:
            hit_rate = (self.cache_stats['hits'] / total_requests) * 100
            print(f"Cache Stats - Size: {len(self.image_cache)}, Hit Rate: {hit_rate:.1f}%, Hits: {self.cache_stats['hits']}, Misses: {self.cache_stats['misses']}, Evictions: {self.cache_stats['evictions']}")
        else:
            print(f"Cache Stats - Size: {len(self.image_cache)}, No requests yet")
    
    def update_duplications_label(self):
        """Update the duplications label with the current group count"""
        if hasattr(self, 'groups') and self.groups:
            group_count = len(self.groups)
            total_duplicates = sum(len(group) - 1 for group in self.groups)
            self.duplications_label.config(text=f"Duplications ({group_count})")
        else:
            self.duplications_label.config(text="Duplications")
    
    def auto_select_all_groups(self):
        """Automatically select all groups in tree view after scan/regroup"""
        if not self.tree:
            return
        
        # Get all top-level group items
        group_items = self.tree.get_children()
        
        # Only auto-select if there are groups (not placeholder)
        if group_items and len(self.groups) > 0:
            # Clear any existing selection
            self.tree.selection_remove(self.tree.selection())
            
            # Select all group items
            self.tree.selection_set(group_items)
            
            # Trigger the selection event to display images
            self.on_tree_select(None)
            
            print(f"[LOG] Auto-selected {len(group_items)} groups in tree view")

    def select_folder(self):
        """Select a folder and count images, but don't start scanning yet"""
        folder = filedialog.askdirectory()
        if folder:
            # Clear cache when selecting new folder to free memory
            self.clear_image_cache()
            
            self.folder = folder
            # Truncate path if too long
            display_path = folder
            if len(display_path) > 35:
                display_path = "..." + display_path[-32:]
            self.lbl_folder.config(text=display_path, fg=self.colors['text_primary'])
            
            # Update trash count when folder is selected
            self.trash_manager.update_trash_count()
            
            # Clear tree
            self.tree.delete(*self.tree.get_children())
            
            # Clear image panel
            for widget in self.img_panel.winfo_children():
                widget.destroy()
            
            # Clear any previous scan data
            self.groups = []
            self.embeddings = {}
            self.files = []
            self.similarity_scores = {}
            
            # Hide re-group button until scan completes
            self.regroup_btn.pack_forget()
            
            # Count image files (excluding Trash folder)
            files = []
            for dp, dn, filenames in os.walk(folder):
                # Skip the Trash directory and its subdirectories
                if "Trash" in dp.split(os.sep):
                    continue
                    
                # Add valid images to the list
                for f in filenames:
                    if os.path.splitext(f)[1].lower() in IMG_EXT:
                        files.append(os.path.join(dp, f))
            total = len(files)
            
            if total == 0:
                self.status_bar.set_text("No images found in selected folder")
                self.lbl_image_count.config(text="No images found", fg=self.colors['danger'])
                self.scan_btn.config(state=tk.DISABLED)
                messagebox.showinfo("No Images", "No images found in the selected folder.")
                return
            
            # Show image count and enable scan button
            self.lbl_image_count.config(text=f"Found {total} images", fg=self.colors['success'])
            self.scan_btn.config(state=tk.NORMAL)
            self.status_bar.set_text(f"Ready to scan {total} images - Click 'Start Scan' to begin")
    
    def start_scan(self):
        """Start scanning the selected folder for duplicates"""
        if not self.folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        
        # Get all image files (excluding Trash folder)
        files = []
        for dp, dn, filenames in os.walk(self.folder):
            # Skip the Trash directory and its subdirectories
            if "Trash" in dp.split(os.sep):
                continue
                
            # Add valid images to the list
            for f in filenames:
                if os.path.splitext(f)[1].lower() in IMG_EXT:
                    files.append(os.path.join(dp, f))
        total = len(files)
        
        if total == 0:
            self.status_bar.set_text("No images found in selected folder")
            messagebox.showinfo("No Images", "No images found in the selected folder.")
            return
        
        # Clear image panel
        for widget in self.img_panel.winfo_children():
            widget.destroy()
        
        # Show progress window
        self.show_progress_window(total)
        
        # Get the threshold value from slider
        threshold = self.threshold_var.get()
        
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
                    self.root.after(0, self.status_bar.set_text, status_bar_text)
                    
                    try:
                        batch_embeddings = get_clip_embedding_batch(batch_files)
                        for f, emb in zip(batch_files, batch_embeddings):
                            embeddings[f] = emb
                    except Exception as e:
                        print(f"Error processing batch {start}-{end}: {e}")
                        continue
                
                # Store embeddings and files for re-grouping
                self.embeddings = embeddings
                self.files = files
                
                # Update progress for duplicate detection phase
                self.update_progress(total, total, "Identifying Duplicates...", 
                                   "Comparing image similarities and grouping duplicates...")
                self.root.after(0, self.status_bar.set_text, "Identifying duplicate groups...")
                
                # Define progress callback for duplicate detection
                def duplicate_progress_callback(current, total_imgs, status_text, detail_text):
                    self.root.after(0, self.update_progress, current, total_imgs, status_text, detail_text)
                    percent = int((current / total_imgs) * 100) if total_imgs > 0 else 100
                    status_bar_text = f"Identifying duplicates: {current}/{total_imgs} ({percent}%)"
                    self.root.after(0, self.status_bar.set_text, status_bar_text)
                
                # Get groups and similarity scores with user-specified threshold
                result = group_similar_images_clip(folder=self.folder, threshold=threshold, 
                                                 embeddings=embeddings, files=files, 
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
                threshold_percent = int(threshold * 100)
                final_status = f"Complete! Found {len(self.groups)} images with duplicates (≥{threshold_percent}% similarity)"
                final_detail = f"Processed {total} images - {total_duplicates} total duplicates found"
                self.update_progress(total, total, final_status, final_detail)
                
                # Update status bar with final result
                final_status_text = f"Done! {len(self.groups)} images have duplicates ({total_duplicates} total) at {threshold_percent}% similarity threshold"
                self.root.after(0, self.status_bar.set_text, final_status_text)
                self.root.after(0, self.status_bar.set_color, "#33cc33", "white")
                
                # Update main UI
                self.populate_tree()
                
                # Show re-group button after successful scan
                self.root.after(0, self.regroup_btn.pack, {'fill': tk.X, 'pady': (10, 0)})
                
                # Automatically select all groups in tree view to display results
                self.root.after(100, self.auto_select_all_groups)
                
                # Close progress window after a short delay
                self.root.after(2000, self.close_progress)
                
            except Exception as e:
                # Handle errors gracefully
                error_msg = f"Error during processing: {str(e)}"
                print(f"[ERROR] {error_msg}")
                
                self.update_progress(0, total, "Processing Failed", error_msg)
                
                # Update status bar with error
                self.root.after(0, self.status_bar.set_text, f"Processing failed: {str(e)}")
                self.root.after(0, self.status_bar.set_color, "#cc3333", "white")
                
                # Close progress window after error
                self.root.after(3000, self.close_progress)
        
        threading.Thread(target=process, daemon=True).start()

    def populate_tree(self):
        import time
        t0 = time.perf_counter()
        print(f"[LOG] Starting tree population: {len(self.groups)} groups")
        
        # Update status bar for tree population
        total_duplicates = sum(len(group) - 1 for group in self.groups)
        self.status_bar.set_text(f"Building tree view for {len(self.groups)} images with duplicates...")
        
        self.tree.delete(*self.tree.get_children())
        
        if not self.groups:
            no_duplicates_id = self.tree.insert("", "end", text="✅ No duplicates found", tags=("no_duplicates",))
            # Update duplications label for no groups case
            self.update_duplications_label()
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
            self.status_bar.set_text(f"Ready - {len(self.groups)} images have duplicates ({total_duplicates} total duplicates)")
        else:
            self.status_bar.set_text("No duplicates found - all images are unique")
        
        # Initialize zoom controls
        self.update_zoom_controls()
        
        # Update duplications label with count
        self.update_duplications_label()

    def on_tree_select(self, event):
        # Prevent recursive calls during refresh operations
        if getattr(self, '_refresh_in_progress', False):
            print(f"[DEBUG] on_tree_select: SKIPPED - refresh in progress")
            return
            
        # Prevent rapid-fire calls by tracking last call time
        import time
        current_time = time.perf_counter()
        if hasattr(self, '_last_tree_select_time'):
            if current_time - self._last_tree_select_time < 0.1:  # 100ms minimum between calls
                print(f"[DEBUG] on_tree_select: SKIPPED - too frequent (last call {current_time - self._last_tree_select_time:.3f}s ago)")
                return
        self._last_tree_select_time = current_time
            
        # Add a processing flag to prevent overlapping calls
        if getattr(self, '_tree_select_processing', False):
            print(f"[DEBUG] on_tree_select: SKIPPED - already processing")
            return
        
        self._tree_select_processing = True
        
        try:
            start_time = time.perf_counter()
            print(f"[DEBUG] on_tree_select: Starting")
        
            selected = self.tree.selection()
            if not selected:
                # Update clean button count for empty selection
                self.update_clean_button_count()
                print(f"[DEBUG] on_tree_select: No selection - {time.perf_counter() - start_time:.3f}s")
                return
        
            # Clear previous images and selection tracking
            step_start = time.perf_counter()
            widgets_to_destroy = self.img_panel.winfo_children()
            for widget in widgets_to_destroy:
                widget.destroy()
            self.selected_check_vars.clear()  # Clear checkbox tracking
            print(f"[DEBUG] on_tree_select: Cleared {len(widgets_to_destroy)} widgets - {time.perf_counter() - step_start:.3f}s")
            
            # Handle both single and multiple selection with unified method
            step_start = time.perf_counter()
            print(f"[DEBUG] on_tree_select: About to call display_groups with {len(selected)} items")
            self.display_groups(selected)
            print(f"[DEBUG] on_tree_select: display_groups completed - {time.perf_counter() - step_start:.3f}s")
            
            # Update clean button count
            step_start = time.perf_counter()
            self.update_clean_button_count()
            print(f"[DEBUG] on_tree_select: Updated clean button count - {time.perf_counter() - step_start:.3f}s")
            
            # Update Select All button text
            self.update_select_all_button_text()
            
            # Update scroll region
            step_start = time.perf_counter()
            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
            print(f"[DEBUG] on_tree_select: Scheduled scroll update - {time.perf_counter() - step_start:.3f}s")
        
            total_time = time.perf_counter() - start_time
            print(f"[DEBUG] on_tree_select: COMPLETE - Total time: {total_time:.3f}s")
        
        finally:
            self._tree_select_processing = False
    
    def display_groups(self, selected_items, force_page=False):
        """Unified method to display images from single or multiple selected groups with group-based paging support"""
        import time
        start_time = time.perf_counter()
        print(f"[DEBUG] display_groups: Starting with {len(selected_items)} selected items")
        
        is_single_group = len(selected_items) == 1
        
        # Choose appropriate thumbnail size and layout
        thumb_size = self.thumb_size if is_single_group else self.multi_thumb_size
        
        # Collect all groups with their images from selected items
        if not force_page:
            self.current_display_groups = []  # Reset the list - now stores groups instead of individual images
            self.current_page = 0  # Reset to first page
            
            for item_id in selected_items:
                item = self.tree.item(item_id)
                
                # Skip if not a group node or if it's a placeholder
                if ('values' in item and item['values']) or "No duplicates found" in item['text'] or "Select a folder" in item['text']:
                    continue
                
                # Get group name
                group_name = item['text']
                
                # Get images for this group
                children = self.tree.get_children(item_id)
                group_images = []
                
                for child in children:
                    child_item = self.tree.item(child)
                    if 'values' in child_item and child_item['values']:
                        img_path = child_item['values'][0]
                        group_images.append(img_path)
                
                # Store the entire group as one unit
                if group_images:
                    self.current_display_groups.append({
                        'name': group_name,
                        'images': group_images
                    })
        
        # Calculate page slice - now paginating by groups, not images
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.current_display_groups))
        page_groups = self.current_display_groups[start_idx:end_idx]
        
        # Update pagination controls
        self.update_page_controls()
        
        # Now display the groups on current page
        current_row = 0
        total_images = 0
        
        for group_data in page_groups:
            group_name = group_data['name']
            img_paths = group_data['images']
            
            # Create group header (only for multiple groups or when showing headers)
            show_header = not is_single_group or len(self.current_display_groups) > 1
            if show_header:
                group_header = tk.Frame(self.img_panel, bg=self.colors['bg_secondary'], height=40)
                group_header.grid(row=current_row, column=0, columnspan=10, sticky='ew', padx=5, pady=(5, 0))
                group_header.grid_propagate(False)
                
                header_label = tk.Label(group_header, 
                                       text=f"{group_name}", 
                                       font=("Segoe UI", 12, "bold"),
                                       bg=self.colors['bg_secondary'],
                                       fg=self.colors['text_primary'])
                header_label.pack(side=tk.LEFT, padx=10, pady=8)
                
                current_row += 1
            
            # Load thumbnails for this group
            group_images = []
            for img_path in img_paths:
                img_tk = self.get_cached_thumbnail(img_path, thumb_size)
                if img_tk:
                    group_images.append((img_tk, img_path))
            
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
        
        # Update status
        step_start = time.perf_counter()
        total_all_groups = len(self.current_display_groups)
        total_all_images = sum(len(g['images']) for g in self.current_display_groups)
        
        if is_single_group:
            self.status_bar.set_text(f"Viewing duplicate group with {total_all_images} images")
        else:
            if total_all_groups > self.page_size:
                displayed_groups = len(page_groups)
                self.status_bar.set_text(f"Page {self.current_page + 1} - Showing {displayed_groups} of {total_all_groups} groups ({total_images} of {total_all_images} images)")
            else:
                self.status_bar.set_text(f"Viewing {total_all_groups} groups with {total_all_images} images")
        print(f"[DEBUG] display_groups: Updated status bar - {time.perf_counter() - step_start:.3f}s")
        
        total_time = time.perf_counter() - start_time
        print(f"[DEBUG] display_groups: COMPLETE - Total images: {total_images}, Total time: {total_time:.3f}s")
    
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
        images_frame.grid(row=row, column=0, columnspan=10, sticky='ew', padx=1, pady=1)
        
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
            card.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
        else:
            card.grid(row=row, column=col, padx=1, pady=1, sticky='nsew')
        
        # Image container
        padding = 1 if is_grid else 1
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
        
        # Add double-click to open full image
        img_canvas.bind('<Double-Button-1>', lambda e, path=img_path: self.open_full_image(path))
        
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
            sim_text = f"Similarity: {similarity:.0%}" if is_grid else f"Similarity: {similarity:.0%}"
            
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
        
        # Calculate and display zoom percentage
        base_width = 180  # Reference width (default thumb_size)
        zoom_level = int((self.thumb_size[0] / base_width) * 100)
        
        # Use common zoom controls component
        self.zoom_controls.update_controls(can_zoom_in, can_zoom_out, zoom_level)
    
    def next_page(self):
        """Navigate to the next page of groups"""
        if not self.current_display_groups:
            return
        
        next_page = self.current_page + 1
        if next_page * self.page_size < len(self.current_display_groups):
            self.current_page = next_page
            # Disable buttons during update to prevent rapid clicks
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            
            # Clear and redisplay with new page
            widgets_to_destroy = self.img_panel.winfo_children()
            for widget in widgets_to_destroy:
                widget.destroy()
            self.selected_check_vars.clear()
            
            selected = self.tree.selection()
            self.display_groups(selected, force_page=True)
            
            # Update scroll region
            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
            self.update_clean_button_count()
            self.update_select_all_button_text()
    
    def prev_page(self):
        """Navigate to the previous page of groups"""
        if not self.current_display_groups:
            return
            
        if self.current_page > 0:
            self.current_page -= 1
            # Disable buttons during update to prevent rapid clicks
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            
            # Clear and redisplay with new page
            widgets_to_destroy = self.img_panel.winfo_children()
            for widget in widgets_to_destroy:
                widget.destroy()
            self.selected_check_vars.clear()
            
            selected = self.tree.selection()
            self.display_groups(selected, force_page=True)
            
            # Update scroll region
            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
            self.update_clean_button_count()
            self.update_select_all_button_text()
    
    def update_page_controls(self):
        """Update pagination control states and labels"""
        if not self.current_display_groups or len(self.current_display_groups) == 0:
            self.page_label.config(text="Page 0 of 0")
            self.prev_page_btn.config(state=tk.DISABLED)
            self.next_page_btn.config(state=tk.DISABLED)
            self.page_frame.pack_forget()  # Hide when no groups
            return
        
        # Show pagination controls only if there are multiple pages
        total_pages = max(1, (len(self.current_display_groups) - 1) // self.page_size + 1)
        
        if total_pages > 1:
            self.page_frame.pack(fill=tk.X, pady=(0, 20))
            self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
            
            # Update button states
            self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            next_enabled = (self.current_page + 1) * self.page_size < len(self.current_display_groups)
            self.next_page_btn.config(state=tk.NORMAL if next_enabled else tk.DISABLED)
        else:
            self.page_frame.pack_forget()  # Hide pagination for single page
    
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
            
            # Redisplay with new thumbnail sizes using unified method (preserve current page)
            self.display_groups(selected, force_page=True)
            
            # Restore checkbox states and apply cross overlays after UI update
            self.root.after(50, lambda: self.restore_checkbox_states(checkbox_states))
                
            # Update scroll region
            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
    
    def handle_ctrl_a(self, event=None):
        """Handle Ctrl+A in tree view to select all groups"""
        if not self.tree:
            return "break"
            
        # Clear current selection
        self.tree.selection_remove(self.tree.selection())
        
        # Get all top-level items (groups) in the tree
        group_items = self.tree.get_children()
        
        # Skip if no groups
        if not group_items:
            return "break"
            
        # Select all group items
        self.tree.selection_set(group_items)
        
        # Trigger the selection event to load all images
        self.on_tree_select(None)
        
        # Prevent default handling of Ctrl+A
        return "break"
        
    def select_all_groups(self):
        """Smart select: when images are displayed, selects only duplicates (keeps originals unchecked)"""
        # If there are image checkboxes visible, use smart selection
        if self.selected_check_vars:
            self.toggle_select_all_images()
        else:
            # Otherwise, select all tree items
            if not self.tree:
                return
                
            # Clear current selection
            self.tree.selection_remove(self.tree.selection())
            
            # Select all top-level items in the tree
            group_items = self.tree.get_children()
            if group_items:
                self.tree.selection_set(group_items)
                self.on_tree_select(None)
            all_items = self.tree.get_children()
            for item in all_items:
                self.tree.selection_add(item)
                
            # Update clean button count
            self.update_clean_button_count()
    
    def clean_selected_images(self):
        """Move selected duplicate images to trash"""
        # Prevent concurrent cleaning operations
        if self._cleaning_in_progress:
            return
            
        # Set cleaning flag
        self._cleaning_in_progress = True
        
        try:
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

                self.move_images_to_trash(images_to_clean)
                # Refresh the display
                self.refresh_after_clean(images_to_clean)
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
                    self.refresh_after_clean(images_to_clean)
                    
        finally:
            # Reset cleaning flag
            self._cleaning_in_progress = False
    
    def move_images_to_trash(self, image_paths):
        """Move images to system trash or create local trash folder"""
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
        
        for img_path in image_paths:
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
                import shutil
                shutil.move(img_path, target_path)
                moved_count += 1
                
                # Remove from data structures
                self.remove_from_groups(img_path)
                    
            except Exception as e:
                print(f"Failed to move {img_path}: {str(e)}")
                failed_files.append(base_name)

        # Store results for refresh_after_clean
        self._last_clean_count = moved_count
        self._last_failed_files = failed_files
        self._trash_dir = trash_dir

    def remove_from_groups(self, img_path):
        """Remove an image path from all groups"""
        for group in self.groups:
            if img_path in group:
                group.remove(img_path)


    
    def update_clean_button_count(self):
        """Update the clean button with the count of selected items"""
        if not hasattr(self, 'clean_btn_var'):
            return
            
        # Priority: Use checkbox selections if available, otherwise use tree selection
        if self.selected_check_vars:
            # Count selected checkboxes
            selected_count = sum(1 for var, _, _ in self.selected_check_vars if var.get())
        elif self.tree:
            # Fall back to tree selection count
            selected_count = len(self.tree.selection())
        else:
            selected_count = 0
            
        self.clean_btn_var.set(f"Clean ({selected_count})")
    
    def update_select_all_button_text(self):
        """Update the Select All button text based on current selection state"""
        if not hasattr(self, 'select_all_btn_var'):
            return
        
        # Check if any images are displayed
        if not self.selected_check_vars:
            self.select_all_btn_var.set("Select All")
            return
        
        # Create a set of first images (ones to keep) from all groups
        first_images = set()
        if hasattr(self, 'groups') and self.groups:
            for group in self.groups:
                if group:  # Make sure group is not empty
                    first_images.add(group[0])  # First image in each group
        
        # Check if any duplicates are currently selected (excluding first images)
        duplicates_selected = any(
            item[0].get() for item in self.selected_check_vars 
            if len(item) >= 2 and item[1] not in first_images
        )
        
        # Update button text based on state
        if duplicates_selected:
            self.select_all_btn_var.set("Unselect All")
        else:
            self.select_all_btn_var.set("Select All")
    
    def on_image_check(self, var, img_path):
        """Handle individual image checkbox selection"""
        # Skip update if we're doing bulk selection to prevent performance issues
        if getattr(self, '_updating_bulk_selection', False):
            return
            
        # Update cross overlay on image
        ImageUtils.update_cross_overlay(self.selected_check_vars, var, img_path, getattr(self, '_trash_icon_cache', None))
            
        # Update clean button count based on selected images
        selected_count = sum(1 for item in self.selected_check_vars 
                           if len(item) >= 2 and item[0].get())
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")
        
        # Update Select All button text
        self.update_select_all_button_text()
    
    def count_selected_images(self):
        """Count how many images are currently selected via checkboxes"""
        return sum(1 for item in self.selected_check_vars 
                  if len(item) >= 2 and item[0].get())
    
    def toggle_select_all_images(self):
        """Smart selection: Keep first image in each group unchecked, select duplicates"""
        if not self.selected_check_vars:
            return
        
        # Create a set of first images (ones to keep) from all groups
        first_images = set()
        if hasattr(self, 'groups') and self.groups:
            for group in self.groups:
                if group:  # Make sure group is not empty
                    first_images.add(group[0])  # First image in each group
        
        # Check if any duplicates are currently selected (excluding first images)
        duplicates_selected = any(
            item[0].get() for item in self.selected_check_vars 
            if len(item) >= 2 and item[1] not in first_images
        )
        
        # If any duplicates are selected, clear all selections
        # If no duplicates are selected, select all duplicates (but keep first images unchecked)
        new_state = not duplicates_selected
        
        # Temporarily disable callback updates to prevent performance issues
        self._updating_bulk_selection = True
        
        try:
            # Apply smart selection logic
            for item in self.selected_check_vars:
                if len(item) >= 2:
                    var, img_path = item[0], item[1]
                    
                    # If this is a first image (original), always keep it unchecked
                    if img_path in first_images:
                        var.set(False)
                    else:
                        # This is a duplicate, apply the toggle state
                        var.set(new_state)
        finally:
            # Re-enable callback updates
            self._updating_bulk_selection = False
        
        # Update all cross overlays
        for item in self.selected_check_vars:
            if len(item) >= 2:
                var, img_path = item[0], item[1]
                ImageUtils.update_cross_overlay(self.selected_check_vars, var, img_path, getattr(self, '_trash_icon_cache', None))
        
        # Update clean button once at the end
        selected_count = self.count_selected_images()
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")
        
        # Update Select All button text based on new state
        if hasattr(self, 'select_all_btn_var'):
            if new_state:
                self.select_all_btn_var.set("Unselect All")
            else:
                self.select_all_btn_var.set("Select All")
    
    def refresh_after_clean(self, cleaned_paths):
        """Efficiently refresh UI after cleaning images"""
        import time
        start_time = time.perf_counter()
        print(f"[DEBUG] refresh_after_clean started - {len(cleaned_paths)} paths to clean")
        
        # Set refresh flag to prevent recursive tree selection events
        self._refresh_in_progress = True
        
        try:
            # Store current selection and expansion state to restore later
            step_start = time.perf_counter()
            current_selection = []
            expansion_state = {}  # group_index -> expanded (True/False)
            print(f"[DEBUG] Step 1: Initialize variables - {time.perf_counter() - step_start:.3f}s")
            
            if hasattr(self, 'tree') and self.tree:
                step_start = time.perf_counter()
                current_selection = self.tree.selection()
                selected_group_indices = []
                print(f"[DEBUG] Step 2: Get current selection ({len(current_selection)} items) - {time.perf_counter() - step_start:.3f}s")
                
                # Store expansion state of all group nodes
                step_start = time.perf_counter()
                siblings = self.tree.get_children("")
                for i, group_item in enumerate(siblings):
                    expansion_state[i] = self.tree.item(group_item, 'open')
                print(f"[DEBUG] Step 3: Store expansion state ({len(siblings)} groups) - {time.perf_counter() - step_start:.3f}s")
                
                # Map current selections to group indices
                step_start = time.perf_counter()
                for selected_item in current_selection:
                    parent = self.tree.parent(selected_item)
                    if parent == "":  # This is a group node
                        # Find the group index by counting siblings
                        group_index = siblings.index(selected_item)
                        selected_group_indices.append(group_index)
                    else:
                        # This is an image node, get parent group index
                        group_index = siblings.index(parent)
                        selected_group_indices.append(group_index)
                print(f"[DEBUG] Step 4: Map selections to indices ({len(selected_group_indices)} mapped) - {time.perf_counter() - step_start:.3f}s")
                
            # Remove cleaned images from groups and update tree
            if hasattr(self, 'groups') and self.groups:
                step_start = time.perf_counter()
                print(f"[DEBUG] Step 5: Starting group cleanup - {len(self.groups)} original groups")
                
                # Remove cleaned images from groups
                updated_groups = []
                group_mapping = []  # Track which old groups correspond to new groups
                
                for old_index, group in enumerate(self.groups):
                    # Filter out cleaned images
                    remaining_images = [img for img in group if img not in cleaned_paths and os.path.exists(img)]
                    # Only keep groups that still have duplicates (2+ images)
                    if len(remaining_images) >= 2:
                        updated_groups.append(remaining_images)
                        group_mapping.append(old_index)  # Map new index to old index
                
                # Update groups and rebuild tree with proper naming
                self.groups = updated_groups
                print(f"[DEBUG] Step 5: Group cleanup complete - {len(updated_groups)} groups remain - {time.perf_counter() - step_start:.3f}s")
                
                # Clear and rebuild tree
                if self.tree:
                    step_start = time.perf_counter()
                    old_children = self.tree.get_children()
                    for item in old_children:
                        self.tree.delete(item)
                    print(f"[DEBUG] Step 6: Clear old tree ({len(old_children)} items) - {time.perf_counter() - step_start:.3f}s")
                    
                    # Rebuild tree with original naming scheme
                    step_start = time.perf_counter()
                    new_group_nodes = []
                    total_images = 0
                    for i, group in enumerate(self.groups):
                        # Use original naming scheme: first filename with duplicate count
                        first_filename = os.path.basename(group[0])
                        duplicate_count = len(group) - 1
                        group_text = f"📂 {first_filename} ({duplicate_count} duplicate{'s' if duplicate_count != 1 else ''})"
                        
                        group_item = self.tree.insert("", "end", text=group_text, open=False)
                        new_group_nodes.append(group_item)
                        
                        for img_path in group:
                            filename = os.path.basename(img_path)
                            self.tree.insert(group_item, "end", text=f"🖼️ {filename}", values=(img_path,))
                            total_images += 1
                    print(f"[DEBUG] Step 7: Rebuild tree ({len(new_group_nodes)} groups, {total_images} images) - {time.perf_counter() - step_start:.3f}s")
                    
                    # Restore expansion state for all groups
                    step_start = time.perf_counter()
                    restored_count = 0
                    for new_index, group_item in enumerate(new_group_nodes):
                        # Find the corresponding old group index
                        if new_index < len(group_mapping):
                            old_group_index = group_mapping[new_index]
                            # Restore the original expansion state
                            if old_group_index in expansion_state:
                                was_expanded = expansion_state[old_group_index]
                                self.tree.item(group_item, open=was_expanded)
                                restored_count += 1
                    print(f"[DEBUG] Step 8: Restore expansion state ({restored_count} restored) - {time.perf_counter() - step_start:.3f}s")
                    
                    # Restore selection based on group mapping
                    step_start = time.perf_counter()
                    items_to_select = []
                    for old_group_index in selected_group_indices:
                        # Find if this old group still exists
                        try:
                            new_index = group_mapping.index(old_group_index)
                            if new_index < len(new_group_nodes):
                                items_to_select.append(new_group_nodes[new_index])
                        except ValueError:
                            # Old group was completely cleaned, skip
                            pass
                    print(f"[DEBUG] Step 9: Map selection ({len(items_to_select)} items to select) - {time.perf_counter() - step_start:.3f}s")
                    
                    # If we have items to select, select them and trigger display
                    step_start = time.perf_counter()
                    if items_to_select:
                        # Simply restore selection - tree selection events are handled by flag
                        for item in items_to_select:
                            self.tree.selection_add(item)
                        
                        # Manually trigger display (bypassing event system entirely)
                        print(f"[DEBUG] Step 10a: Restore selection - {time.perf_counter() - step_start:.3f}s")
                        step_start = time.perf_counter()
                        
                        # Call display_groups directly instead of on_tree_select to avoid event loops
                        selected = self.tree.selection()
                        if selected:
                            # Clear previous images
                            widgets_to_destroy = self.img_panel.winfo_children()
                            for widget in widgets_to_destroy:
                                widget.destroy()
                            self.selected_check_vars.clear()
                            # Display the selected groups
                            self.display_groups(selected)
                            self.update_clean_button_count()
                            self.update_select_all_button_text()
                            self.root.after(10, lambda: self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all")))
                        
                        print(f"[DEBUG] Step 10b: Trigger display (direct call) - {time.perf_counter() - step_start:.3f}s")
                    else:
                        # No valid selection, clear image display
                        img_widgets = self.img_panel.winfo_children()
                        for widget in img_widgets:
                            widget.destroy()
                        self.selected_check_vars.clear()
                        print(f"[DEBUG] Step 10: Clear display ({len(img_widgets)} widgets cleared) - {time.perf_counter() - step_start:.3f}s")
                    
                    # Update scroll region
                    step_start = time.perf_counter()
                    self.img_canvas.configure(scrollregion=self.img_canvas.bbox("all"))
                    print(f"[DEBUG] Step 11: Update scroll region - {time.perf_counter() - step_start:.3f}s")
                    
                    # Update clean button count
                    step_start = time.perf_counter()
                    self.update_clean_button_count()
                    print(f"[DEBUG] Step 12: Update clean button count - {time.perf_counter() - step_start:.3f}s")
                    
                    # Update trash count
                    step_start = time.perf_counter()
                    self.trash_manager.update_trash_count()
                    print(f"[DEBUG] Step 13: Update trash count - {time.perf_counter() - step_start:.3f}s")
                    
                    # Update duplications label
                    step_start = time.perf_counter()
                    self.update_duplications_label()
                    print(f"[DEBUG] Step 14: Update duplications label - {time.perf_counter() - step_start:.3f}s")
                    
                    # Update status
                    step_start = time.perf_counter()
                    if hasattr(self, 'status_bar'):
                        self.status_bar.set_text(f"Cleaned images. {len(self.groups)} duplicate groups remaining.")
                    print(f"[DEBUG] Step 15: Update status bar - {time.perf_counter() - step_start:.3f}s")

            # Show modern completion popup - TEMPORARILY DISABLED FOR DEBUGGING
            step_start = time.perf_counter()
            # self.show_clean_completion_popup()  # DISABLED
            print(f"[DEBUG] Step 16: Show completion popup (SKIPPED) - {time.perf_counter() - step_start:.3f}s")
            
            total_time = time.perf_counter() - start_time
            print(f"[DEBUG] refresh_after_clean COMPLETE - Total time: {total_time:.3f}s")
            
        except Exception as e:
            total_time = time.perf_counter() - start_time
            print(f"[DEBUG] refresh_after_clean ERROR after {total_time:.3f}s: {e}")
            print(f"Error during refresh: {e}")
            # Fallback to simple message
            messagebox.showinfo("Clean Complete", "Images moved to trash. Please refresh manually if needed.")
        
        finally:
            # Always clear the refresh flag
            self._refresh_in_progress = False
            print(f"[DEBUG] refresh_after_clean: Refresh flag cleared")
            
            # TEMPORARY FIX: Disable tree selection events for 2 seconds to prevent infinite loops
            if hasattr(self, 'tree') and self.tree:
                self.tree.unbind("<<TreeviewSelect>>")
                print(f"[DEBUG] refresh_after_clean: Tree selection events DISABLED for 2 seconds")
                
                def re_enable_selection():
                    if hasattr(self, 'tree') and self.tree:
                        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
                        print(f"[DEBUG] refresh_after_clean: Tree selection events RE-ENABLED")
                
                self.root.after(2000, re_enable_selection)  # Re-enable after 2 seconds

    def show_clean_completion_popup(self):
        """Show simple, fast completion message without blocking"""
        import time
        step_start = time.perf_counter()
        print(f"[DEBUG] show_clean_completion_popup: Starting SIMPLIFIED popup creation")
        
        try:
            # Get clean results
            moved_count = getattr(self, '_last_clean_count', 0)
            failed_files = getattr(self, '_last_failed_files', [])
            
            # Create simple message
            if failed_files and len(failed_files) > 0:
                title = "Partial Success"
                message = f"Moved {moved_count} images to Trash\nFailed to move {len(failed_files)} files"
            else:
                title = "Clean Complete"
                message = f"Successfully moved {moved_count} images to Trash"
            
            print(f"[DEBUG] show_clean_completion_popup: Using simple messagebox instead of complex popup")
            
            # Use simple, reliable messagebox instead of complex custom popup
            # This runs asynchronously and won't block
            def show_async_message():
                try:
                    messagebox.showinfo(title, message)
                    print(f"[DEBUG] show_clean_completion_popup: Simple messagebox completed")
                except Exception as e:
                    print(f"[DEBUG] show_clean_completion_popup: Messagebox error: {e}")
            
            # Schedule the messagebox to appear after a short delay (non-blocking)
            self.root.after(100, show_async_message)
            
            print(f"[DEBUG] show_clean_completion_popup: Simple popup scheduled - {time.perf_counter() - step_start:.3f}s")
            
        except Exception as e:
            print(f"[DEBUG] show_clean_completion_popup: ERROR - {str(e)}")
            print(f"Error showing popup: {str(e)}")
        
        print(f"[DEBUG] show_clean_completion_popup: Method complete - {time.perf_counter() - step_start:.3f}s")

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
                    ImageUtils.update_cross_overlay(self.selected_check_vars, var, img_path, getattr(self, '_trash_icon_cache', None))
        
        # Update clean button count
        selected_count = self.count_selected_images()
        if hasattr(self, 'clean_btn_var'):
            self.clean_btn_var.set(f"Clean ({selected_count})")

    def open_full_image(self, img_path):
        """Open image in full-size window using common utility"""
        ImageUtils.open_full_image(self.root, img_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageIdentifierApp(root)
    root.mainloop()
