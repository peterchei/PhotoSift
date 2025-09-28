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
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, xscrollcommand=tree_xscroll.set)
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Center frame for image and controls
        center_frame = tk.Frame(main_frame)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.img_panel = tk.Label(center_frame)
        self.img_panel.pack(pady=10)
        self.lbl_result = tk.Label(center_frame, text="", font=("Arial", 14))
        self.lbl_result.pack(pady=5)
        nav = tk.Frame(center_frame)
        nav.pack()
        tk.Button(nav, text="< Prev", command=self.prev_img).pack(side=tk.LEFT)
        tk.Button(nav, text="Next >", command=self.next_img).pack(side=tk.LEFT)
    # Removed category buttons as requested

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
        item = self.tree.item(selected[0])
        # Only leaf nodes (images) have 'values'
        if 'values' in item and item['values']:
            path = item['values'][0]
            # Find index in current list
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

    def show_img(self):
        img_list = self.get_current_list()
        if not img_list:
            self.img_panel.config(image=None)
            self.img_panel.image = None
            self.lbl_result.config(text="No images in this category.")
            return
        path = img_list[self.current]
        img = Image.open(path).resize((400, 300))
        img_tk = ImageTk.PhotoImage(img)
        self.img_panel.config(image=img_tk)
        self.img_panel.image = img_tk
        label, conf, _ = classify_people_vs_screenshot(path)
        self.lbl_result.config(text=f"{os.path.basename(path)}: {label} ({conf:.2f})")

    def next_img(self):
        img_list = self.get_current_list()
        if img_list and self.current < len(img_list) - 1:
            self.current += 1
            self.show_img()

    def prev_img(self):
        img_list = self.get_current_list()
        if img_list and self.current > 0:
            self.current -= 1
            self.show_img()

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
