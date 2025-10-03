
# Standard library imports
import os
import threading

# Third-party imports
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# Local imports
from ImageClassification import classify_people_vs_screenshot, IMG_EXT
from ImageClassification import classify_people_vs_screenshot_batch

class ImageClassifierApp:
    def select_all_photos(self):
        # Select all checkboxes in the current thumbnail view
        if hasattr(self, 'selected_check_vars'):
            for var, _ in self.selected_check_vars:
                var.set(True)
            self.update_clean_btn_label(self.count_selected_photos())
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

        self.thumb_canvas = tk.Canvas(self.right_frame, bg="#f9fafb", highlightthickness=0, bd=0)
        self.thumb_scrollbar = tk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=14)
        self.thumbs_frame = tk.Frame(self.thumb_canvas, bg="#f9fafb")
        self.thumb_canvas.create_window((0,0), window=self.thumbs_frame, anchor="nw")
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
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

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.lbl_folder.config(text=folder)
            self.images = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                           for f in filenames if os.path.splitext(f)[1].lower() in IMG_EXT]
            self.people_images = []
            self.screenshot_images = []
            self.image_labels = {}  # path -> label
            total = len(self.images)
            self.status_bar.config(bg="#3399ff", fg="white")
            self.status_var.set(f"Processing 0/{total} images (0%)...")
            self.root.update_idletasks()

            import threading
            def process_images():
                from ImageClassification import classify_people_vs_screenshot_batch
                batch_size = 64  # Increase batch size for better GPU utilization
                for start in range(0, total, batch_size):
                    end = min(start + batch_size, total)
                    batch_paths = self.images[start:end]
                    percent = int((end/total)*100) if total else 100
                    print(f"[LOG] Processing images {start+1}-{end}/{total} ({percent}%)")
                    self.root.after(0, self.status_var.set, f"Processing images {start+1}-{end}/{total} ({percent}%)")
                    self.root.after(0, self.status_bar.config, {"bg": "#3399ff", "fg": "white"})
                    batch_results = classify_people_vs_screenshot_batch(batch_paths)
                    for p, result in zip(batch_paths, batch_results):
                        if result is None:
                            print(f"[WARN] Skipping image due to load/classify failure: {p}")
                            continue
                        label, conf, _ = result
                        self.image_labels[p] = label
                        if label == "people":
                            self.people_images.append(p)
                        elif label == "screenshot":
                            self.screenshot_images.append(p)
                people_count = len(self.people_images)
                screenshot_count = len(self.screenshot_images)
                self.root.after(0, self.status_var.set, f"Done processing {total} images. (100%) | People: {people_count} | Screenshot: {screenshot_count}")
                self.root.after(0, self.status_bar.config, {"bg": "#33cc33", "fg": "white"})
                self.current = 0
                self.current_list = "all"
                self.root.after(0, self.populate_tree)
                if self.images:
                    self.root.after(0, self.show_img)
                else:
                    self.root.after(0, lambda: messagebox.showinfo("No Images", "No images found in folder."))
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
    def show_selected_thumbnails(self, paths):
        # Clear previous thumbnails
        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.img_panel.pack_forget()
        self.lbl_result.pack_forget()
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.center_frame.pack_forget()
        self.selected_check_vars = []
        self.update_clean_btn_label(0)
        for idx, img_path in enumerate(paths):
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
                # Rounded frame and hover effect
                frame = tk.Frame(self.thumbs_frame, bd=0, bg="#f9fafb", highlightbackground="#e0e6ef", highlightthickness=2)
                frame.grid(row=idx//5, column=idx%5, padx=12, pady=12)
                lbl_img = tk.Label(frame, image=img_tk, bg="#f9fafb")
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_img.bind('<Double-Button-1>', lambda e, p=img_path: self.open_full_image(p))
                # Hover effect for thumbnail
                def on_enter(ev, f=frame):
                    f.config(bg="#e3eafc", highlightbackground="#a5d8fa")
                def on_leave(ev, f=frame):
                    f.config(bg="#f9fafb", highlightbackground="#e0e6ef")
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                lbl_img.bind("<Enter>", on_enter)
                lbl_img.bind("<Leave>", on_leave)
                var = tk.BooleanVar()
                chk = tk.Checkbutton(frame, text=os.path.basename(img_path), variable=var, command=lambda v=var, p=img_path: self.on_image_check(v, p), font=("Arial", 10), bg="#f9fafb", activebackground="#e3eafc", selectcolor="#a5d8fa", bd=0, highlightthickness=0)
                chk.pack(pady=4)
                self.selected_check_vars.append((var, img_path))
                var.trace_add('write', lambda *args: self.update_clean_btn_label(self.count_selected_photos()))
            except Exception:
                continue
        self.thumb_canvas.update_idletasks()
        self.thumb_canvas.yview_moveto(0)

    def count_selected_photos(self):
        return sum(var.get() for var, _ in self.selected_check_vars)

    def update_clean_btn_label(self, count):
        self.clean_btn_var.set(f"Clean ({count})")

    def clean_selected_photos(self):
        # Placeholder for clean action
        selected = [img_path for var, img_path in self.selected_check_vars if var.get()]
        messagebox.showinfo("Clean", f"You selected {len(selected)} photo(s) to clean.\nPaths: {selected}")

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

    def on_image_check(self, var, path):
        if var.get():
            messagebox.showinfo("Image Selected", f"Selected: {os.path.basename(path)}")

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
