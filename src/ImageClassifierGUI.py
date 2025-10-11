
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
from CommonUI import (ToolTip, ModernColors, ProgressWindow, ModernStyling, 
                     StatusBar, ZoomControls, ModernButton)

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
                    img = Image.open(img_path)
                    img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = img_tk
                self.thumb_imgs.append(img_tk)
                
                # Modern card with rounded corners
                card = tk.Frame(self.thumbs_frame, bd=0, 
                               bg=self.colors['bg_card'], 
                               highlightbackground=self.colors['bg_secondary'], 
                               highlightthickness=1,
                               relief=tk.SOLID)
                card.grid(row=idx//4, column=idx%4, padx=15, pady=15, sticky="nsew")
                
                # Configure grid weights for responsive layout
                self.thumbs_frame.grid_columnconfigure(idx%4, weight=1)
                
                # Image container with padding
                img_container = tk.Frame(card, bg=self.colors['bg_card'])
                img_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 8))
                
                # Modern image label
                lbl_img = tk.Label(img_container, image=img_tk, bg=self.colors['bg_card'], bd=0)
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_img.bind('<Double-Button-1>', lambda e, p=img_path: self.open_full_image(p))
                
                # Modern hover effects
                def on_enter(ev, c=card):
                    c.config(highlightbackground=self.colors['accent'], highlightthickness=2)
                def on_leave(ev, c=card):
                    c.config(highlightbackground=self.colors['bg_secondary'], highlightthickness=1)
                
                card.bind("<Enter>", on_enter)
                card.bind("<Leave>", on_leave)
                lbl_img.bind("<Enter>", on_enter)
                lbl_img.bind("<Leave>", on_leave)
                
                # Info section at bottom
                info_frame = tk.Frame(card, bg=self.colors['bg_card'])
                info_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
                
                # Checkbox and filename
                var = tk.BooleanVar()
                filename = os.path.basename(img_path)
                if len(filename) > 25:
                    filename = filename[:22] + "..."
                    
                chk = tk.Checkbutton(info_frame, 
                                   text=filename, 
                                   variable=var,
                                   command=lambda v=var, p=img_path: self.on_image_check(v, p),
                                   font=("Segoe UI", 10, "bold"), 
                                   bg=self.colors['bg_card'],
                                   fg=self.colors['text_primary'],
                                   activebackground=self.colors['bg_card'],
                                   selectcolor=self.colors['accent'], 
                                   bd=0, highlightthickness=0,
                                   anchor="w")
                chk.pack(fill=tk.X, pady=(0, 4))
                
                # Confidence score with color coding
                if img_path in self.confidence_scores:
                    confidence = self.confidence_scores[img_path]
                    conf_text = f"Confidence: {confidence:.0%}"
                    
                    # Color code based on confidence
                    if confidence >= 0.9:
                        conf_color = self.colors['success']
                    elif confidence >= 0.7:
                        conf_color = self.colors['accent']
                    elif confidence >= 0.5:
                        conf_color = self.colors['warning']
                    else:
                        conf_color = self.colors['danger']
                    
                    conf_label = tk.Label(info_frame, 
                                        text=conf_text, 
                                        font=("Segoe UI", 9),
                                        bg=self.colors['bg_card'], 
                                        fg=conf_color,
                                        anchor="w")
                    conf_label.pack(fill=tk.X)
                
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
        self.root.title("Find Out Photo Unwanted")
        # Maximize window on startup
        self.root.state('zoomed')  # Windows maximized state
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
        
        # Use centralized color scheme
        self.colors = ModernColors.get_color_scheme()
        
        # Initialize progress window
        self.progress_window = ProgressWindow(self.root, "AI Image Classification")
        
        self.setup_ui()
        
        # Apply modern styling using common component
        ModernStyling.apply_modern_styling(self.colors)
        
        # Apply dark theme after UI setup with multiple attempts
        self.root.after(100, self.apply_dark_theme_fix)
        self.root.after(500, self.apply_dark_theme_fix)  # Second attempt
        self.root.after(1000, self.apply_dark_theme_fix)  # Third attempt

    def apply_dark_theme_fix(self):
        """Ensure dark theme is properly applied to all components"""
        try:
            print("Applying dark theme fix...")
            
            # Force tree styling using multiple approaches
            style = ttk.Style()
            
            # Configure both default and custom Treeview styles
            treeview_config = {
                'fieldbackground': self.colors['bg_card'],
                'background': self.colors['bg_card'], 
                'foreground': self.colors['text_primary'],
                'borderwidth': 0,
                'lightcolor': self.colors['bg_card'],
                'darkcolor': self.colors['bg_card'],
                'selectbackground': self.colors['accent'],
                'selectforeground': self.colors['text_primary']
            }
            
            # Apply to both default and custom styles
            style.configure("Treeview", **treeview_config)
            style.configure("Modern.Treeview", **treeview_config)
            
            # Also set the map for selection states
            style.map("Treeview",
                     background=[('selected', self.colors['accent']), ('active', self.colors['bg_secondary'])],
                     foreground=[('selected', self.colors['text_primary']), ('active', self.colors['text_primary'])])
            
            style.map("Modern.Treeview", 
                     background=[('selected', self.colors['accent']), ('active', self.colors['bg_secondary'])],
                     foreground=[('selected', self.colors['text_primary']), ('active', self.colors['text_primary'])])
            
            # Force apply the style
            self.tree.configure(style="Modern.Treeview")
            
            # Try direct widget configuration as backup
            try:
                self.tree.configure(background=self.colors['bg_card'])
            except Exception as widget_error:
                print(f"Direct widget config failed: {widget_error}")
            
            # Update the placeholder text to force a refresh
            if hasattr(self, 'tree_placeholder_id'):
                try:
                    self.tree.item(self.tree_placeholder_id, 
                                  text="📁 Select a folder to start classification")
                except:
                    pass
            
            # Update display
            self.root.update_idletasks()
            print("Dark theme fix applied successfully")
            
        except Exception as e:
            print(f"Theme fix error: {e}")

    def setup_ui(self):
        import tkinter.ttk as ttk
        
        # Colors are now loaded in __init__ from ModernColors
        
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
                                 text="Find Out Photo Unwanted", 
                                 font=("Segoe UI", 14),
                                 bg=self.colors['bg_primary'], 
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(anchor="w")

        # Header buttons frame
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
        
        # Main content container
        content = tk.Frame(self.root, bg=self.colors['bg_primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 20))

        # Modern sidebar
        sidebar = tk.Frame(content, bg=self.colors['bg_sidebar'], width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        sidebar.pack_propagate(False)
        
        # Folder selection section
        folder_section = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        folder_section.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        # Modern select folder button
        select_btn = tk.Button(folder_section, 
                              text="Select Folder", 
                              command=self.select_folder,
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors['accent'],
                              fg=self.colors['text_primary'],
                              activebackground=self.colors['accent_hover'],
                              activeforeground=self.colors['text_primary'],
                              bd=0, relief=tk.FLAT, cursor="hand2",
                              padx=20, pady=10)
        select_btn.pack(fill=tk.X)
        
        # Folder path display
        self.lbl_folder = tk.Label(folder_section, 
                                  text="No folder selected", 
                                  bg=self.colors['bg_sidebar'], 
                                  font=("Segoe UI", 10), 
                                  fg=self.colors['text_secondary'],
                                  wraplength=260,
                                  justify=tk.LEFT)
        self.lbl_folder.pack(fill=tk.X, pady=(8, 0))
        
        # Categories section
        categories_section = tk.Frame(sidebar, bg=self.colors['bg_sidebar'])
        categories_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        categories_label = tk.Label(categories_section, 
                                   text="Categories", 
                                   bg=self.colors['bg_sidebar'], 
                                   font=("Segoe UI", 14, "bold"), 
                                   fg=self.colors['text_primary'])
        categories_label.pack(anchor="w", pady=(0, 10))
        
        # Tree frame with dark theme
        tree_frame = tk.Frame(categories_section, bg=self.colors['bg_card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a wrapper frame for the tree with dark background
        tree_wrapper = tk.Frame(tree_frame, bg=self.colors['bg_card'], bd=0, highlightthickness=0)
        tree_wrapper.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Modern TTK scrollbars matching image view style
        tree_scroll = ttk.Scrollbar(tree_wrapper, 
                                   orient=tk.VERTICAL,
                                   style="Modern.Vertical.TScrollbar")
        tree_xscroll = ttk.Scrollbar(tree_wrapper, 
                                    orient=tk.HORIZONTAL,
                                    style="Modern.Horizontal.TScrollbar")
        
        # Modern treeview with explicit styling
        self.tree = ttk.Treeview(tree_wrapper, 
                                yscrollcommand=tree_scroll.set, 
                                xscrollcommand=tree_xscroll.set, 
                                selectmode="extended", 
                                show="tree")
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Configure modern styling
        tree_style = ttk.Style()
        
        # Set a dark theme as base - try multiple themes
        try:
            # Try different themes that work better with dark styling
            available_themes = tree_style.theme_names()
            # Try themes in order of best dark support
            if 'clam' in available_themes:
                tree_style.theme_use('clam')
                print("Using 'clam' theme for better dark styling")
            elif 'alt' in available_themes:
                tree_style.theme_use('alt')
                print("Using 'alt' theme")
            else:
                print("Using default theme")
        except Exception as e:
            print(f"Theme error: {e}")
            pass  # Fall back to default if theme not available
        
        # Modern treeview styling with proper colors
        tree_style.configure("Modern.Treeview", 
                           rowheight=28, 
                           fieldbackground=self.colors['bg_card'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           borderwidth=0,
                           relief="flat",
                           insertcolor=self.colors['text_primary'],
                           focuscolor=self.colors['accent'])
        
        # Configure treeview item padding and colors
        tree_style.configure("Modern.Treeview.Item", 
                           padding=(12, 4, 12, 4),
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'])
        
        # Configure selection colors
        tree_style.map("Modern.Treeview",
                      background=[('selected', self.colors['accent']),
                                ('active', self.colors['bg_secondary'])],
                      foreground=[('selected', self.colors['text_primary']),
                                ('active', self.colors['text_primary'])])
        
        # Apply the modern style immediately
        self.tree.configure(style="Modern.Treeview")
        
        # Force update the tree styling
        self.root.update_idletasks()
        
        # Modern scrollbar styling
        tree_style.configure("Modern.Vertical.TScrollbar",
                           background=self.colors['bg_secondary'],
                           troughcolor=self.colors['bg_primary'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_secondary'],
                           darkcolor=self.colors['bg_secondary'],
                           lightcolor=self.colors['bg_secondary'])
        
        # Horizontal scrollbar styling
        tree_style.configure("Modern.Horizontal.TScrollbar",
                           background=self.colors['bg_secondary'],
                           troughcolor=self.colors['bg_primary'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_secondary'],
                           darkcolor=self.colors['bg_secondary'],
                           lightcolor=self.colors['bg_secondary'])
        
        # Configure tag styles for placeholder
        self.tree.tag_configure("placeholder", 
                               foreground=self.colors['text_secondary'],
                               background=self.colors['bg_card'])
        
        # Add placeholder content to show proper styling immediately
        placeholder_id = self.tree.insert("", "end", 
                                         text="📁 Select a folder to start classification", 
                                         tags=("placeholder",))
        
        # Store placeholder ID for later removal
        self.tree_placeholder_id = placeholder_id
        
        # Force another update to ensure styling is applied
        self.root.update_idletasks()

        # Modern main area
        main_area = tk.Frame(content, bg=self.colors['bg_primary'])
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Navigation bar
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
                                       command=self.select_all_photos,
                                       font=("Segoe UI", 12, "bold"),
                                       bg=self.colors['accent'],
                                       fg=self.colors['text_primary'],
                                       activebackground=self.colors['accent_hover'],
                                       bd=0, relief=tk.FLAT, cursor="hand2",
                                       padx=16, pady=8)
        self.select_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Modern Clean button
        self.clean_btn_var = tk.StringVar()
        self.clean_btn_var.set("Clean (0)")
        self.clean_btn = tk.Button(action_frame, 
                                  textvariable=self.clean_btn_var,
                                  command=self.clean_selected_photos,
                                  font=("Segoe UI", 12, "bold"),
                                  bg=self.colors['danger'],
                                  fg=self.colors['text_primary'],
                                  activebackground='#dc2626',
                                  bd=0, relief=tk.FLAT, cursor="hand2",
                                  padx=16, pady=8)
        self.clean_btn.pack(side=tk.LEFT)
        
        # Main content area
        self.right_frame = tk.Frame(main_area, bg=self.colors['bg_primary'])
        self.right_frame.pack(fill=tk.BOTH, expand=True)

        # Modern pagination controls
        self.page_frame = tk.Frame(self.right_frame, bg=self.colors['bg_primary'], height=50)
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
        
        self.page_label = tk.Label(nav_center, text="Page 1 of 5", 
                                  font=("Segoe UI", 12, "bold"), 
                                  bg=self.colors['bg_primary'], 
                                  fg=self.colors['text_primary'])
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_page_btn = tk.Button(nav_center, text="Next →", command=self.next_page, **nav_btn_style)
        self.next_page_btn.pack(side=tk.LEFT, padx=(15, 0))
        
        self.page_frame.pack_forget()  # Hide initially
        
        # Main container for thumbnails
        self.content_frame = tk.Frame(self.right_frame, bg=self.colors['bg_primary'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Modern thumbnail container
        self.thumb_container = tk.Frame(self.content_frame, bg=self.colors['bg_primary'])
        self.thumb_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Modern canvas and scrollbar
        self.thumb_canvas = tk.Canvas(self.thumb_container, 
                                     bg=self.colors['bg_primary'], 
                                     highlightthickness=0, 
                                     bd=0)
        
        # Modern styled scrollbar
        self.thumb_scrollbar = ttk.Scrollbar(self.thumb_container, 
                                           orient=tk.VERTICAL, 
                                           command=self.thumb_canvas.yview,
                                           style="Modern.Vertical.TScrollbar")
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create modern thumbs frame
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg=self.colors['bg_primary'])
        self.thumb_canvas.create_window((0,0), window=self.thumbs_frame, anchor="nw")
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        
        # Simple mouse wheel scrolling
        def _on_mousewheel(event):
            self.thumb_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.thumbs_frame.bind("<MouseWheel>", _on_mousewheel)
        self.thumb_container.bind("<MouseWheel>", _on_mousewheel)
        self.thumb_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Enable mouse wheel scrolling with error handling
        def on_mousewheel(event):
            try:
                scroll_amount = -1 if event.delta > 0 else 1
                self.thumb_canvas.yview_scroll(scroll_amount, "units")
            except Exception as e:
                print(f"Scroll error: {str(e)}")
                
        # Bind mouse wheel events safely
        try:
            self.thumb_canvas.bind_all("<MouseWheel>", on_mousewheel)
        except Exception as e:
            print(f"Binding error: {str(e)}")
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            if event.state == 0:  # No modifier keys
                # Regular scroll
                self.thumb_canvas.yview_scroll(-1 * (event.delta // 120), "units")
            elif event.state == 1:  # Shift key for horizontal scroll
                # Horizontal scroll
                self.thumb_canvas.xview_scroll(-1 * (event.delta // 120), "units")
                
        # Bind mouse wheel for Windows (MouseWheel) and macOS/Linux (Button-4/Button-5)
        self.thumb_canvas.bind("<MouseWheel>", on_mousewheel)  # Windows
        self.thumb_canvas.bind("<Button-4>", lambda e: self.thumb_canvas.yview_scroll(-1, "units"))  # Linux/macOS scroll up
        self.thumb_canvas.bind("<Button-5>", lambda e: self.thumb_canvas.yview_scroll(1, "units"))   # Linux/macOS scroll down
        
        # Also bind the thumbnails frame for better event capture
        self.thumbs_frame.bind("<MouseWheel>", on_mousewheel)
        self.thumbs_frame.bind("<Button-4>", lambda e: self.thumb_canvas.yview_scroll(-1, "units"))
        self.thumbs_frame.bind("<Button-5>", lambda e: self.thumb_canvas.yview_scroll(1, "units"))
        
        self.content_frame.pack_forget()  # Hide initially
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg=self.colors['bg_primary'])
        self.thumb_canvas.create_window((0,0), window=self.thumbs_frame, anchor="nw")
        # Configure frame for layout updates
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_canvas.bind("<Configure>", self.on_canvas_configure)
        self.thumb_imgs = []
        self.right_frame.pack_forget()  # Hide initially

        # Center frame for single image view
        self.center_frame = tk.Frame(main_area, bg=self.colors['bg_primary'])
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Modern image panel
        self.img_panel = tk.Label(self.center_frame, 
                                 bg=self.colors['bg_primary'], 
                                 bd=0)
        self.img_panel.pack(pady=(40, 16), ipadx=6, ipady=6)
        
        # Modern result label
        self.lbl_result = tk.Label(self.center_frame, 
                                  text="", 
                                  font=("Segoe UI", 18, "bold"), 
                                  bg=self.colors['bg_primary'], 
                                  fg=self.colors['text_primary'])
        self.lbl_result.pack(pady=10)

        # Create status bar using common component
        self.status_bar = StatusBar(self.root, self.colors, "Ready - Select a folder to classify images")

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
        # Create modern progress window
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Processing Images")
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
                                      text="Initializing AI Classification...", 
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

    def update_progress(self, current, total, status_text, detail_text):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_var.set(current)
            self.progress_label.config(text=status_text)
            self.progress_detail.config(text=detail_text)
            self.progress_window.update_idletasks()

    def close_progress(self):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()

    def open_trash_folder(self):
        if self.folder:
            trash_path = os.path.join(self.folder, "Trash")
            if os.path.exists(trash_path):
                os.startfile(trash_path)  # Windows specific
            else:
                messagebox.showinfo("Trash Folder", "Trash folder does not exist yet.")
        else:
            messagebox.showinfo("Trash Folder", "Please select a folder first.")
    
    def update_trash_count(self):
        if self.folder:
            trash_path = os.path.join(self.folder, "Trash")
            if os.path.exists(trash_path):
                # Count image files in trash
                count = sum(1 for f in os.listdir(trash_path) 
                         if os.path.isfile(os.path.join(trash_path, f)) 
                         and os.path.splitext(f)[1].lower() in IMG_EXT)
                self.trash_count = count
                self.trash_btn_var.set(f"Trash ({count})")
            else:
                self.trash_count = 0
                self.trash_btn_var.set("Trash (0)")
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            # Show shorter path for better display
            display_path = folder
            if len(display_path) > 50:
                parts = display_path.split(os.sep)
                if len(parts) > 3:
                    display_path = f"...{os.sep}{os.sep.join(parts[-2:])}"
            
            self.lbl_folder.config(text=display_path, fg=self.colors['text_primary'])
            self.update_trash_count()  # Update trash count when folder is selected
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
            self.status_bar.set_text(f"Processing 0/{total} images (0%)...")
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
                    self.root.after(0, self.status_bar.set_text, f"Processing images {start+1}-{end}/{total} ({percent}%)")
                    
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
                self.root.after(0, self.status_bar.set_text, f"Done processing {total} images. (100%) | People: {people_count} | Screenshot: {screenshot_count}")
                self.root.after(0, self.status_bar.set_color, "#33cc33", "white")
                
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
        # Clear all existing items including placeholder
        self.tree.delete(*self.tree.get_children())
        
        people_count = len(self.people_images)
        screenshot_count = len(self.screenshot_images)
        people_node = self.tree.insert("", "end", text=f"People ({people_count})", open=False)  # Collapsed by default
        for p in self.people_images:
            # Add confidence score to the display text
            confidence = self.confidence_scores.get(p, 0.0)
            display_text = f"{os.path.basename(p)} ({confidence:.2f})"
            self.tree.insert(people_node, "end", text=display_text, values=(p,))
        screenshot_node = self.tree.insert("", "end", text=f"Screenshot ({screenshot_count})", open=True)  # Expanded by default
        for p in self.screenshot_images:
            # Add confidence score to the display text
            confidence = self.confidence_scores.get(p, 0.0)
            display_text = f"{os.path.basename(p)} ({confidence:.2f})"
            self.tree.insert(screenshot_node, "end", text=display_text, values=(p,))
        
        # Select the Screenshot node by default
        if screenshot_count > 0:
            self.tree.selection_set(screenshot_node)
            self.tree.focus(screenshot_node)
            # Trigger the selection event to show screenshot images
            self.on_tree_select(None)
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
        
        # Show pagination if there are multiple pages
        total_pages = max(1, (len(self.current_paths) - 1) // self.page_size + 1)
        if total_pages > 1:
            self.page_frame.pack(fill=tk.X, pady=(0, 20))
        else:
            self.page_frame.pack_forget()
        
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
                    img = Image.open(img_path)
                    img.thumbnail(self.thumb_size, Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.image_cache[cache_key] = img_tk
                self.thumb_imgs.append(img_tk)
                
                # Update zoom level indicator
                base_width = 240  # Reference width
                zoom_level = int((self.thumb_size[0] / base_width) * 100)
                self.zoom_label.config(text=f"Zoom: {zoom_level}%")
                
                # Calculate layout position
                cols = self.calculate_columns()
                
                # Create modern dark theme card
                frame = tk.Frame(self.thumbs_frame, bd=0, 
                               bg=self.colors['bg_card'], 
                               highlightbackground=self.colors['bg_secondary'], 
                               highlightthickness=1,
                               relief=tk.SOLID)
                frame.grid(row=idx//cols, column=idx%cols, padx=6, pady=6, sticky='nsew')
                
                # Image container with reduced padding
                img_container = tk.Frame(frame, bg=self.colors['bg_card'])
                img_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))
                
                lbl_img = tk.Label(img_container, image=img_tk, bg=self.colors['bg_card'], bd=0)
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_img.bind('<Double-Button-1>', lambda e, p=img_path: self.open_full_image(p))
                
                # Modern hover animations
                def on_enter(ev, f=frame):
                    f.config(highlightbackground=self.colors['accent'], highlightthickness=2)
                    
                def on_leave(ev, f=frame):
                    f.config(highlightbackground=self.colors['bg_secondary'], highlightthickness=1)
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                lbl_img.bind("<Enter>", on_enter)
                lbl_img.bind("<Leave>", on_leave)
                
                var = tk.BooleanVar()
                # Create frame for text (filename and confidence)
                text_frame = tk.Frame(frame, bg=self.colors['bg_card'])
                text_frame.pack(fill=tk.X, padx=4, pady=(0, 4))
                
                # Filename checkbox with modern styling
                filename = os.path.basename(img_path)
                if len(filename) > 25:
                    filename = filename[:22] + "..."
                
                chk = tk.Checkbutton(text_frame, 
                                   text=filename, 
                                   variable=var, 
                                   command=lambda v=var, p=img_path: self.on_image_check(v, p), 
                                   font=("Segoe UI", 9, "bold"), 
                                   bg=self.colors['bg_card'],
                                   fg=self.colors['text_primary'],
                                   activebackground=self.colors['bg_card'], 
                                   selectcolor=self.colors['accent'], 
                                   bd=0, highlightthickness=0)
                chk.pack(anchor="w", pady=(0, 2))
                
                # Confidence score with color coding
                if img_path in self.confidence_scores:
                    conf_score = self.confidence_scores[img_path]
                    conf_text = f"Confidence: {conf_score:.0%}"
                    
                    # Color code based on confidence
                    if conf_score >= 0.9:
                        conf_color = self.colors['success']
                    elif conf_score >= 0.7:
                        conf_color = self.colors['accent']
                    elif conf_score >= 0.5:
                        conf_color = self.colors['warning']
                    else:
                        conf_color = self.colors['danger']
                    
                    conf_label = tk.Label(text_frame, 
                                        text=conf_text, 
                                        font=("Segoe UI", 8), 
                                        bg=self.colors['bg_card'], 
                                        fg=conf_color,
                                        cursor="question_arrow")
                    conf_label.pack(anchor="w")
                    
                    # Create tooltip with confidence explanation
                    category = self.image_labels.get(img_path, "unknown")
                    tooltip_text = self.get_confidence_tooltip(conf_score, category)
                    ToolTip(conf_label, tooltip_text)
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
        thumb_space = self.thumb_size[0] + 12  # thumbnail width + reduced padding
        
        # Calculate number of columns that can fit
        return max(1, canvas_width // thumb_space)
    
    def get_confidence_tooltip(self, confidence, category):
        """Generate helpful tooltip text for confidence scores"""
        if confidence >= 0.9:
            level = "Very High"
            explanation = "The AI is very confident about this classification."
        elif confidence >= 0.75:
            level = "High"
            explanation = "The AI is confident about this classification."
        elif confidence >= 0.6:
            level = "Moderate"
            explanation = "The AI has moderate confidence. Consider reviewing this image."
        elif confidence >= 0.4:
            level = "Low"
            explanation = "The AI has low confidence. This image may be misclassified."
        else:
            level = "Very Low"
            explanation = "The AI has very low confidence. This image is likely misclassified."
        
        tooltip = f"Confidence: {confidence:.2f} ({level})\n"
        tooltip += f"Category: {category.title()}\n"
        tooltip += explanation
        
        if confidence < 0.6:
            tooltip += "\n\nTip: Lower confidence scores may indicate the image doesn't clearly fit either category."
        
        return tooltip
    
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

        # Show professional popup message
        try:
            popup = tk.Toplevel()
            popup.title("Operation Status")
            
            # Make the window float on top
            popup.lift()
            popup.attributes('-topmost', True)
            
            # Enhanced window setup
            window_width = 380
            window_height = 150
            
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
            
            # Configure window style
            popup.configure(bg='#ffffff')
            popup.overrideredirect(True)  # Remove window decorations
            
            # Create main container with border
            border_frame = tk.Frame(popup, bg='#e2e8f0', padx=1, pady=1)
            border_frame.pack(fill=tk.BOTH, expand=True)
            
            main_frame = tk.Frame(border_frame, bg='#ffffff')
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header bar
            header_frame = tk.Frame(main_frame, bg='#f8fafc', height=32)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            header_label = tk.Label(header_frame, text="Operation Complete",
                                  bg='#f8fafc', fg='#334155',
                                  font=("Segoe UI", 11, "bold"))
            header_label.pack(side=tk.LEFT, padx=15, pady=6)
            
            # Content frame with padding
            content_frame = tk.Frame(main_frame, bg='#ffffff', padx=20, pady=15)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Status icon and colors
            if failed_files:
                icon = "⚠"
                title = "Partial Success"
                icon_color = "#dc2626"  # Red
                message = f"Moved {moved_count} photos to Trash\n"
                if len(failed_files) > 0:
                    message += f"Failed to move {len(failed_files)} files"
            else:
                icon = "✓"
                title = "Success"
                icon_color = "#0369a1"  # Blue
                message = f"Successfully moved {moved_count} photos to Trash"
            
            # Icon
            icon_label = tk.Label(content_frame, text=icon, bg='#ffffff',
                                fg=icon_color, font=("Segoe UI", 24))
            icon_label.pack(pady=(0, 5))
            
            # Title
            title_label = tk.Label(content_frame, text=title, bg='#ffffff',
                                 fg=icon_color, font=("Segoe UI", 12, "bold"))
            title_label.pack(pady=(0, 8))
            
            # Message
            msg_label = tk.Label(content_frame, text=message, bg='#ffffff',
                               fg='#475569', font=("Segoe UI", 11))
            msg_label.pack()
            
            # Force the window to update and show
            popup.update()
            
            # Add subtle fade out before destruction
            def fade_out():
                for i in range(10):
                    opacity = 1.0 - (i / 10)
                    popup.attributes('-alpha', opacity)
                    popup.update()
                    popup.after(50)
                popup.destroy()
            
            # Schedule fade out and destruction
            popup.after(1500, fade_out)
            
        except Exception as e:
            print(f"Error showing popup: {str(e)}")
            messagebox.showinfo("Clean Complete", 
                              f"Moved {moved_count} photos to Trash")
        
        # Auto-close after 1 second
        popup.after(1000, popup.destroy)

        # Refresh UI
        self.populate_tree()  # Update the category tree
        self.update_trash_count()  # Update the trash count
        
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
        if frame:
            if var.get():
                # Selected state - blue accent highlight
                frame.config(bg=self.colors['bg_card'], 
                           highlightbackground=self.colors['accent'], 
                           highlightthickness=3)
            else:
                # Unselected state - default dark theme colors
                frame.config(bg=self.colors['bg_card'], 
                           highlightbackground=self.colors['bg_secondary'], 
                           highlightthickness=1)
        
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
