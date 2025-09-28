import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
from DuplicateImageIdentifier import group_similar_images_clip, IMG_EXT

class DuplicateImageIdentifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Identifier")
        self.folder = None
        self.groups = []
        self.setup_ui()

    def setup_ui(self):
        import tkinter.ttk as ttk
        frm = tk.Frame(self.root)
        frm.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(frm, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT)
        self.lbl_folder = tk.Label(frm, text="No folder selected")
        self.lbl_folder.pack(side=tk.LEFT, padx=10)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Treeview for groups
        tree_frame = tk.Frame(main_frame, width=200)
        tree_frame.grid(row=0, column=0, sticky="ns")
        tree_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_xscroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, xscrollcommand=tree_xscroll.set)
        tree_scroll.config(command=self.tree.yview)
        tree_xscroll.config(command=self.tree.xview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Center frame for image display
        center_frame = tk.Frame(main_frame)
        center_frame.grid(row=0, column=1, sticky="nsew")
        self.img_panel = tk.Frame(center_frame)
        self.img_panel.pack(pady=10, fill=tk.BOTH, expand=True)
        self.lbl_result = tk.Label(center_frame, text="", font=("Arial", 14))
        self.lbl_result.pack(pady=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#f0f0f0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.lbl_folder.config(text=folder)
            # Get all image files first
            files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                     for f in filenames if os.path.splitext(f)[1].lower() in IMG_EXT]
            total = len(files)
            self.status_bar.config(bg="#3399ff", fg="white")
            self.status_var.set(f"Processing 0/{total} images (0%)...")
            self.root.update_idletasks()
            # Group similar images with progress (efficient)
            import threading
            def process():
                from DuplicateImageIdentifier import get_clip_embedding_batch, group_similar_images_clip
                embeddings = {}
                batch_size = 64
                for start in range(0, total, batch_size):
                    end = min(start + batch_size, total)
                    batch_files = files[start:end]
                    percent = int((end/total)*100) if total else 100
                    print(f"[LOG] Processing images {start+1}-{end}/{total} ({percent}%)")
                    self.status_var.set(f"Processing images {start+1}-{end}/{total} ({percent}%)")
                    self.status_bar.config(bg="#3399ff", fg="white")
                    self.root.update_idletasks()
                    try:
                        batch_embeddings = get_clip_embedding_batch(batch_files)
                        for f, emb in zip(batch_files, batch_embeddings):
                            embeddings[f] = emb
                    except Exception as e:
                        print(f"Error processing batch {start}-{end}: {e}")
                        continue
                self.status_var.set(f"Done processing {total} images. (100%) | Identifying duplications....")
                self.root.update_idletasks()
                self.groups = group_similar_images_clip(folder=folder, embeddings=embeddings, files=files)
                self.status_var.set(f"Done processing {total} images. (100%) | Duplicates found: {len(self.groups)}")
                self.status_bar.config(bg="#33cc33", fg="white")
                self.populate_tree()
            threading.Thread(target=process).start()

    def populate_tree(self):
        import time
        t0 = time.perf_counter()
        print(f"[LOG] Starting tree population: {len(self.groups)} groups")
        self.tree.delete(*self.tree.get_children())
        for i, group in enumerate(self.groups, 1):
            group_node = self.tree.insert("", "end", text=f"Group {i} ({len(group)})", open=True)
            if len(group) > 100:
                print(f"[LOG] Group {i} is large ({len(group)} images), inserting in chunks...")
                chunk_size = 100
                for start in range(0, len(group), chunk_size):
                    end = min(start + chunk_size, len(group))
                    for img_path in group[start:end]:
                        self.tree.insert(group_node, "end", text=os.path.basename(img_path), values=(img_path,))
            else:
                for img_path in group:
                    self.tree.insert(group_node, "end", text=os.path.basename(img_path), values=(img_path,))
        print(f"[LOG] Finished tree population in {time.perf_counter()-t0:.2f}s")

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        # If group node (no 'values'), show all images in group
        if not ('values' in item and item['values']):
            # Clear previous thumbnails
            for widget in self.img_panel.winfo_children():
                widget.destroy()
            # Find group images
            children = self.tree.get_children(selected[0])
            images = []
            for child in children:
                img_path = self.tree.item(child)['values'][0]
                try:
                    img = Image.open(img_path).resize((120, 90))
                    img_tk = ImageTk.PhotoImage(img)
                    images.append((img_tk, img_path))
                except Exception:
                    continue
            # Display thumbnails
            for idx, (img_tk, img_path) in enumerate(images):
                frame = tk.Frame(self.img_panel)
                frame.grid(row=idx//4, column=idx%4, padx=5, pady=5)
                lbl_img = tk.Label(frame, image=img_tk)
                lbl_img.image = img_tk
                lbl_img.pack()
                lbl_name = tk.Label(frame, text=os.path.basename(img_path), font=("Arial", 10))
                lbl_name.pack()
            self.lbl_result.config(text=f"Group: {item['text']}")
        # If leaf node, show single image
        elif 'values' in item and item['values']:
            path = item['values'][0]
            for widget in self.img_panel.winfo_children():
                widget.destroy()
            img = Image.open(path).resize((400, 300))
            img_tk = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.img_panel, image=img_tk)
            lbl.image = img_tk
            lbl.pack()
            self.lbl_result.config(text=os.path.basename(path))

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateImageIdentifierApp(root)
    root.mainloop()
