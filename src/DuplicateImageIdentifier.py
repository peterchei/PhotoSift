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

def group_similar_images_clip(folder=None, threshold=0.95, embeddings=None, files=None, progress_callback=None):
    # Accept precomputed embeddings and file list for efficiency
    if files is None:
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                 for f in filenames if Path(f).suffix.lower() in IMG_EXT]
    if embeddings is None:
        # Use batch embedding extraction for all files
        emb_array = get_clip_embedding_batch(files)
        embeddings = {f: emb_array[i] for i, f in enumerate(files)}
    
    # Convert embeddings to numpy array for vectorized operations
    file_list = list(files)
    embedding_matrix = np.array([embeddings[f] for f in file_list])
    
    # Normalize embeddings once for cosine similarity
    norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
    normalized_embeddings = embedding_matrix / norms
    
    # Compute full similarity matrix using vectorized operations
    if progress_callback:
        progress_callback(0, len(file_list), "Computing Similarity Matrix...", 
                        "Calculating all pairwise similarities using vectorized operations...")
    
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
    
    # Find duplicate groups using the precomputed similarity matrix
    groups = []
    used = set()
    total_files = len(file_list)
    
    for i, f1 in enumerate(file_list):
        if i in used:
            continue
            
        # Find all similar images for this one using the precomputed matrix
        similar_indices = np.where(similarity_matrix[i] >= threshold)[0]
        
        # Filter out already used indices and self
        group_indices = [idx for idx in similar_indices if idx not in used and idx != i]
        
        if len(group_indices) > 0:  # Only create group if there are duplicates
            group = [f1] + [file_list[idx] for idx in group_indices]
            groups.append(group)
            
            # Mark all images in this group as used
            used.add(i)
            used.update(group_indices)
        else:
            used.add(i)
        
        # Progress update
        if progress_callback and (i + 1) % 50 == 0:
            percent = int(((i + 1) / total_files) * 100)
            progress_callback(i + 1, total_files, f"Grouping Duplicates... ({percent}%)", 
                            f"Processed {i + 1}/{total_files} images: {os.path.basename(f1)}")
    
    # Final progress update
    if progress_callback:
        progress_callback(total_files, total_files, "Duplicate Grouping Complete!", 
                        f"Found {len(groups)} duplicate groups from {total_files} images")
    
    return groups

if __name__ == "__main__":
    folder = "test_image"  # change as needed
    groups = group_similar_images_clip(folder)
    for i, group in enumerate(groups, 1):
        print(f"Group {i}:")
        for f in group:
            print(f"  {f}")
        print()
