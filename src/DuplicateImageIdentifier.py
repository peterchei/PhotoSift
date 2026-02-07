import os
import sys
import logging
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import torch
from transformers import CLIPModel, CLIPProcessor
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logger = logging.getLogger(__name__)

# Device configuration
device = "cuda" if torch.cuda.is_available() else "cpu"

# Supported image extensions
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Global model and processor variables for lazy loading
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
            # Fallback
            model_path = "openai/clip-vit-base-patch32"
            
    return model_path

def load_models():
    """Lazy load models only when needed"""
    global model, processor
    if model is None or processor is None:
        try:
            model_path = get_model_path()
            logger.info(f"Loading CLIP model from: {model_path}")
            model = CLIPModel.from_pretrained(model_path).to(device).eval()
            processor = CLIPProcessor.from_pretrained(model_path)
        except Exception as e:
            logger.error(f"Error loading CLIP model: {e}")
            raise e

def load_image_cv(path, size=(224, 224)):
    """Load image with Unicode path support and high-quality resizing"""
    try:
        # Use PIL to load the image first (handles Unicode paths properly)
        img = Image.open(path).convert("RGB")
        
        # Resize using PIL's high-quality resampling
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        logger.warning(f"Failed to load image {path}: {e}")
        return Image.new("RGB", size)

def get_clip_embedding_batch(img_paths, size=(224, 224)):
    """Extract CLIP embeddings for a batch of images"""
    # Ensure models are loaded
    load_models()
    
    # Parallel image loading
    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(lambda p: load_image_cv(p, size), img_paths))
    
    # Prepare inputs
    inputs = processor(images=images, return_tensors="pt", padding=True)
    
    # Generate embeddings
    with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
        image_features = model.get_image_features(**{k: v.to(device) for k, v in inputs.items()})
        # Handle cases where model returns an object instead of a tensor (common in newer transformers)
        if hasattr(image_features, "pooler_output"):
            image_features = image_features.pooler_output
    
    return image_features.cpu().numpy()

def get_clip_embedding(img_path):
    """Extract CLIP embedding for a single image (legacy support)"""
    return get_clip_embedding_batch([img_path])[0]

def group_similar_images_clip(folder=None, threshold=0.95, embeddings=None, files=None, progress_callback=None, return_scores=False):
    """Group images by visual similarity using CLIP embeddings"""
    # Acceptance of precomputed data
    if files is None:
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder)
                 for f in filenames if Path(f).suffix.lower() in IMG_EXT]
    
    if not files:
        return ([], {}) if return_scores else []

    if embeddings is None:
        # Use batch embedding extraction
        emb_array = get_clip_embedding_batch(files)
        embeddings = {f: emb_array[i] for i, f in enumerate(files)}
    
    # Convert embeddings to matrix
    file_list = list(files)
    embedding_matrix = np.array([embeddings[f] for f in file_list])
    
    # Normalize
    norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
    normalized_embeddings = embedding_matrix / (norms + 1e-8)
    
    # Pairwise similarity
    if progress_callback:
        progress_callback(0, len(file_list), "Computing Similarities...", "Processing similarity matrix")
    
    similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)
    
    # Grouping logic
    groups = []
    similarity_scores = {}
    used = set()
    total_files = len(file_list)
    
    for i, f1 in enumerate(file_list):
        if i in used:
            continue
            
        similar_indices = np.where(similarity_matrix[i] >= threshold)[0]
        group_indices = [idx for idx in similar_indices if idx not in used and idx != i]
        
        if len(group_indices) > 0:
            group = [f1] + [file_list[idx] for idx in group_indices]
            groups.append(group)
            
            for idx in group_indices:
                similarity_scores[file_list[idx]] = float(similarity_matrix[i][idx])
            similarity_scores[f1] = 1.0
            
            used.add(i)
            used.update(group_indices)
        else:
            used.add(i)
        
        if progress_callback and (i + 1) % 50 == 0:
            progress_callback(i + 1, total_files, "Grouping...", f"Processed {i+1}/{total_files}")
    
    if return_scores:
        return groups, similarity_scores
    else:
        return groups

if __name__ == "__main__":
    # Test stub
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()
    
    groups = group_similar_images_clip(args.folder)
    for i, g in enumerate(groups):
        print(f"Group {i}: {g}")
