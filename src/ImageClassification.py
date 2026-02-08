import os, glob, time, sys
from pathlib import Path
import logging

import torch, numpy as np
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

# Setup logging
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"

def get_model_path():
    # Check if running in PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        model_path = os.path.join(base_path, 'models', 'clip-vit-base-patch32')
    else:
        # First check if we have local model files
        local_path = os.path.join('models', 'clip-vit-base-patch32')
        if os.path.exists(local_path):
            model_path = local_path
        else:
            # Fall back to downloading from HuggingFace
            model_path = "openai/clip-vit-base-patch32"
    return model_path


model = None
processor = None

def load_models():
    global model, processor
    if model is None or processor is None:
        try:
            model_path = get_model_path()
            logger.info(f"Loading CLIP from {model_path}")
            model = CLIPModel.from_pretrained(model_path).to(device).eval()
            processor = CLIPProcessor.from_pretrained(model_path)
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise e

def _ensure_tensor(obj):
    """Helper to extract a raw tensor from various ModelOutput containers"""
    if torch.is_tensor(obj):
        return obj
    
    # Try common CLIP/Vision attributes
    for attr in ["logits_per_image", "pooler_output", "last_hidden_state"]:
        val = getattr(obj, attr, None)
        if val is not None and torch.is_tensor(val):
            return val
            
    # Try dictionary-like access
    try:
        for key in ["logits_per_image", "pooler_output", "last_hidden_state"]:
            if key in obj and obj[key] is not None:
                return obj[key]
    except:
        pass
        
    # Try indexing (tuple-like)
    try:
        if len(obj) > 0 and torch.is_tensor(obj[0]):
            return obj[0]
    except:
        pass
        
    return obj

LABELS = {
    "people": [
        "a photo of a person", "a photo of people",
        "a portrait photo", "a candid photo of a person",
        "a group photo", "a selfie", "a family photo", "a photo of friends",
        "a photo of a child", "a photo of an adult", "photo of scenery"
    ],
    "screenshot": [
        "a computer screenshot", "a phone screenshot",
        "a screen capture of an app UI", "a screenshot of a website",
        "a screenshot of a video call", "a screenshot of a chat conversation",
        "a screenshot of a social media post", "a screenshot of a text message",
        "a screenshot of an email", "a screenshot of a document", 
        "a photo of a computer screen", "a photo of a phone screen"
    ],
}


def classify_people_vs_screenshot(path: str):
    # For backward compatibility, single image
    results = classify_people_vs_screenshot_batch([path])
    return results[0] if results else None


def _load_image(path):
    from PIL import Image
    try:
        if os.path.isdir(path):
            return None
        img = Image.open(path).convert("RGB")
        img = img.resize((224, 224), Image.BICUBIC)
        return img
    except Exception as e:
        logger.warning(f"Failed to load image: {path} ({e})")
        return None

def classify_people_vs_screenshot_batch(paths):
    # Parallel image loading
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(_load_image, paths))
    
    # Filter out failed images (None)
    valid = [(img, path) for img, path in zip(images, paths) if img is not None]
    if not valid:
        return [None] * len(paths)
        
    valid_images, valid_paths = zip(*valid)
    
    texts, owners = [], []
    for lbl, prompts in LABELS.items():
        for p in prompts:
            texts.append(p)
            owners.append(lbl)
    
    # Ensure model is loaded
    load_models()
    
    inputs = processor(text=texts, images=list(valid_images), return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
        outputs = model(**inputs)
        out = _ensure_tensor(outputs)
        
        # Logits per image is what we want for classification
        if hasattr(outputs, "logits_per_image"):
            out = outputs.logits_per_image
            
        probs = out.softmax(dim=-1).float().cpu().numpy()  # [batch, num_prompts]
        
    owners = np.array(owners)
    results = []
    for prob in probs:
        scores = {lbl: float(prob[owners == lbl].sum()) for lbl in LABELS}
        pred = max(scores, key=scores.get)
        results.append((pred, scores[pred], scores))
    
    # Map results back to original paths
    final_results = []
    valid_map = dict(zip(valid_paths, results))
    for orig_path in paths:
        final_results.append(valid_map.get(orig_path))
        
    return final_results


IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def classify_folder(folder: str):
    t0 = time.perf_counter()
    files = [p for p in glob.glob(os.path.join(folder, "**", "*"), recursive=True)
             if Path(p).suffix.lower() in IMG_EXT]
    for p in files:
        result = classify_people_vs_screenshot(p)
        if result:
            label, conf, _ = result
            print(f"{p} -> {label} ({conf:.3f})")
    print(f"Done {len(files)} images in {time.perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()
    classify_folder(args.folder)
