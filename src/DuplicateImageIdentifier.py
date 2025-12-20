import os
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
from transformers import CLIPModel, CLIPProcessor
from concurrent.futures import ThreadPoolExecutor

device = "cuda" if torch.cuda.is_available() else "cpu"
import sys
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
from transformers import CLIPModel, CLIPProcessor
from concurrent.futures import ThreadPoolExecutor
import logging

device = "cuda" if torch.cuda.is_available() else "cpu"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

model = None
processor = None

def get_model_path():
    """Get the correct path to the model whether running as script or frozen exe"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
        model_path = os.path.join(base_path, 'models', 'clip-vit-base-patch32')
    else:
        # Running as script - look for local models folder first
        local_path = os.path.join('models', 'clip-vit-base-patch32')
        if os.path.exists(local_path):
            model_path = local_path
        else:
            # Fallback (though in production this should be avoided)
            model_path = "openai/clip-vit-base-patch32"
            
    return model_path

def load_models():
    """Lazy load models only when needed"""
    global model, processor
    if model is None or processor is None:
        try:
            model_path = get_model_path()
            print(f"Loading CLIP model from: {model_path}")
            model = CLIPModel.from_pretrained(model_path).to(device).eval()
            processor = CLIPProcessor.from_pretrained(model_path)
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            # If local load fails, try catch and re-raise or handle
            raise e

def load_image_cv(path, size=(224, 224)):
    """Load image with Unicode path support (handles Chinese/special characters)"""
    try:
        # Use PIL to load the image first (handles Unicode paths properly)
        img = Image.open(path).convert("RGB")
        
        # Resize using PIL's high-quality resampling
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        print(f"Warning: Failed to load image {path}: {e}")
        # Return a blank image as fallback (should rarely happen)
        return Image.new("RGB", size)

def get_clip_embedding_batch(img_paths, size=(224, 224)):
    # Ensure models are loaded
    load_models()
    
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
    load_models()
    img = Image.open(img_path).convert("RGB").resize((224, 224), Image.BICUBIC)
    inputs = processor(images=img, return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**{k: v.to(device) for k, v in inputs.items()})
    return image_features.squeeze().cpu().numpy()

def group_similar_images_clip(folder=None, threshold=0.95, embeddings=None, files=None, progress_callback=None, return_scores=False):
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
    similarity_scores = {}  # Store similarity scores for each image
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
            
            # Store similarity scores for this group (relative to the first image)
            for idx in group_indices:
                file_path = file_list[idx]
                similarity_scores[file_path] = float(similarity_matrix[i][idx])
            
            # First image in group gets maximum score (1.0)
            similarity_scores[f1] = 1.0
            
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
    
    if return_scores:
        return groups, similarity_scores
    else:
        return groups

if __name__ == "__main__":
    folder = "test_image"  # change as needed
    groups = group_similar_images_clip(folder)
    for i, group in enumerate(groups, 1):
        print(f"Group {i}:")
        for f in group:
            print(f"  {f}")
        print()
