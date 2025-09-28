import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from ImageClassification import classify_people_vs_screenshot, IMG_EXT

class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Identifier")
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
        # Top frame for folder selection
        frm = tk.Frame(self.root)
        frm.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(frm, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT)
        self.lbl_folder = tk.Label(frm, text="No folder selected")
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        # Main frame for tree and image
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview with vertical scrollbar on left
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        tree_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_xscroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, xscrollcommand=tree_xscroll.set, selectmode="extended")
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right frame for selected thumbnails with buttons
        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumb_canvas = tk.Canvas(self.right_frame)
        self.thumb_scrollbar = tk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scrollbar.set)
        self.thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.thumbs_frame = tk.Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0,0), window=self.thumbs_frame, anchor="nw")
        self.thumbs_frame.bind("<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all")))
        self.thumb_imgs = []
        self.right_frame.pack_forget()  # Hide initially

        # Center frame for image and controls
        center_frame = tk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.img_panel = tk.Label(center_frame)
        self.img_panel.pack(pady=10)
        self.lbl_result = tk.Label(center_frame, text="", font=("Arial", 14))
        self.lbl_result.pack(pady=5)
        # Removed navigation buttons as requested

        # Status bar at bottom, full width
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#f0f0f0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

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
                    for p, (label, conf, _) in zip(batch_paths, batch_results):
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
        # Gather all selected image paths
        selected_paths = []
        for sel in selected:
            item = self.tree.item(sel)
            if 'values' in item and item['values']:
                selected_paths.append(item['values'][0])
        if selected_paths:
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
                self.show_img()
    def show_selected_thumbnails(self, paths):
        # Clear previous thumbnails
        for widget in self.thumbs_frame.winfo_children():
            widget.destroy()
        self.thumb_imgs.clear()
        self.img_panel.pack_forget()
        self.lbl_result.pack_forget()
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.selected_check_vars = []
        for idx, img_path in enumerate(paths):
            try:
                # Use cache if available
                if img_path in self.image_cache:
                    img_tk = self.image_cache[img_path]
                else:
                    img = Image.open(img_path).resize((120, 90))
                    img_tk = ImageTk.PhotoImage(img)
                    self.image_cache[img_path] = img_tk
                self.thumb_imgs.append(img_tk)
                frame = tk.Frame(self.thumbs_frame, bd=2, relief=tk.RIDGE)
                frame.grid(row=idx//3, column=idx%3, padx=8, pady=8)
                lbl_img = tk.Label(frame, image=img_tk)
                lbl_img.image = img_tk
                lbl_img.pack()
                var = tk.BooleanVar()
                chk = tk.Checkbutton(frame, text="Select", variable=var, command=lambda v=var, p=img_path: self.on_image_check(v, p))
                chk.pack(pady=2)
                self.selected_check_vars.append((var, img_path))
                lbl_name = tk.Label(frame, text=os.path.basename(img_path), font=("Arial", 9))
                lbl_name.pack()
            except Exception:
                continue
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
        if path in self.image_cache:
            img_tk = self.image_cache[path]
        else:
            img = Image.open(path).resize((400, 300))
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[path] = img_tk
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
