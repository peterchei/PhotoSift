import os
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
from transformers import CLIPModel, CLIPProcessor
from concurrent.futures import ThreadPoolExecutor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def load_image_cv(path, size=(224, 224)):
    arr = cv2.imread(path)
    if arr is not None:
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        arr = cv2.resize(arr, size, interpolation=cv2.INTER_AREA)
        return Image.fromarray(arr)
    return Image.new("RGB", size)

def get_clip_embedding_batch(img_paths, size=(224, 224)):
    with ThreadPoolExecutor(max_workers=16) as executor:
        images = list(executor.map(lambda p: load_image_cv(p, size), img_paths))
    inputs = processor(images=images, return_tensors="pt", padding=True)
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
        image_features = model.get_image_features(**{k: v.to(device) for k, v in inputs.items()})
    return image_features.cpu().numpy()
import os
from pathlib import Path
from PIL import Image
import numpy as np

import torch
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def get_clip_embedding(img_path):
    img = Image.open(img_path).convert("RGB").resize((224, 224), Image.BICUBIC)
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**{k: v.to(device) for k, v in inputs.items()})
    return image_features.squeeze().cpu().numpy()

def group_similar_images_clip(folder=None, threshold=0.95, embeddings=None, files=None):
    # Accept precomputed embeddings and file list for efficiency
    if files is None:
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                 for f in filenames if Path(f).suffix.lower() in IMG_EXT]
    if embeddings is None:
        # Use batch embedding extraction for all files
        emb_array = get_clip_embedding_batch(files)
        embeddings = {f: emb_array[i] for i, f in enumerate(files)}
    groups = []
    used = set()
    for f1 in files:
        if f1 in used:
            continue
        group = [f1]
        emb1 = embeddings[f1]
        for f2 in files:
            if f2 == f1 or f2 in used:
                continue
            emb2 = embeddings[f2]
            sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            if sim >= threshold:
                group.append(f2)
                used.add(f2)
        used.add(f1)
        if len(group) > 1:
            groups.append(group)
    return groups

if __name__ == "__main__":
    folder = "test_image"  # change as needed
    groups = group_similar_images_clip(folder)
    for i, group in enumerate(groups, 1):
        print(f"Group {i}:")
        for f in group:
            print(f"  {f}")
        print()
