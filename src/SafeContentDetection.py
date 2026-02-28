"""
Safe Content Detection
Uses CLIP to classify images into 4 categories: safe, adult, violent, disturbing.
Entirely local — no data sent to the internet. CLIP model is already bundled.
"""

import os
import sys
from pathlib import Path

import torch
import numpy as np
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"


def get_model_path():
    """Return the path to the CLIP model, preferring local bundle over HuggingFace."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        model_path = os.path.join(base_path, 'models', 'clip-vit-base-patch32')
    else:
        local_path = os.path.join('models', 'clip-vit-base-patch32')
        if os.path.exists(local_path):
            model_path = local_path
        else:
            model_path = "openai/clip-vit-base-patch32"
    return model_path


model = None
processor = None


def load_models():
    """Lazily load CLIP model and processor."""
    global model, processor
    if model is None or processor is None:
        try:
            model_path = get_model_path()
            print(f"Loading CLIP from {model_path}")
            model = CLIPModel.from_pretrained(model_path).to(device).eval()
            processor = CLIPProcessor.from_pretrained(model_path)
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise e


LABELS = {
    "safe": [
        "a family-friendly photo appropriate for children",
        "a wholesome photo of people smiling",
        "a photo of nature, landscape, or scenery",
        "a photo of food, pets, or everyday objects",
        "a travel or vacation photo",
        "a group photo at a family event",
        "a photo of children playing outdoors",
        "an ordinary innocent photo",
        "a photo of a birthday party or celebration",
        "a photo of a school or sporting event",
    ],
    "adult": [
        "explicit sexual content or adult nudity",
        "pornographic or sexually explicit imagery",
        "adult content not suitable for minors",
        "erotic or sexual imagery",
        "partial or full nudity in a sexual context",
        "adult-only content",
        "sexually suggestive imagery",
        "intimate adult content",
    ],
    "violent": [
        "violent or graphic content with blood or injuries",
        "gore or bloody imagery",
        "a photo showing severe physical harm or wounds",
        "graphic violence, fighting, or combat",
        "a photo depicting injury or death",
        "disturbing imagery of physical violence",
        "war or battlefield graphic content",
        "a photo of a serious accident with injuries",
    ],
    "disturbing": [
        "disturbing or shocking content not suitable for children",
        "offensive imagery that would upset a child",
        "drug use or illegal substance imagery",
        "a photo of a crime scene",
        "hateful or extremist symbols or imagery",
        "a frightening or deeply unsettling photo",
        "content depicting self-harm",
        "dark and disturbing occult imagery",
    ],
}

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

# Confidence threshold for definitive vs. hedged ratings
_CONFIDENCE_THRESHOLD = 0.6


class SafeContentDetector:
    """Wraps CLIP for 4-category safe content classification."""

    def classify_image(self, image_path):
        """
        Classify a single image.

        Returns:
            (predicted_label, confidence, all_scores)
            predicted_label: one of 'safe', 'adult', 'violent', 'disturbing'
            confidence: 0.0-1.0 (sum of prompts for winning category)
            all_scores: {'safe': float, 'adult': float, ...}
            Returns ('error', 0.0, {}) on failure.
        """
        results = scan_content_batch([image_path])
        if not results:
            return ('error', 0.0, {})
        _path, label, confidence, all_scores = results[0]
        return (label, confidence, all_scores)

    def get_content_rating(self, label, confidence):
        """
        Map label + confidence to a human-readable rating string.

        Examples:
            ('safe',      0.95) -> 'Safe'
            ('adult',     0.80) -> 'Adult Content'
            ('violent',   0.70) -> 'Violent / Gore'
            ('disturbing',0.65) -> 'Disturbing'
            ('safe',      0.51) -> 'Likely Safe'
            ('adult',     0.40) -> 'Possibly Adult'
        """
        if label == 'safe':
            return 'Safe' if confidence >= _CONFIDENCE_THRESHOLD else 'Likely Safe'
        elif label == 'adult':
            return 'Adult Content' if confidence >= _CONFIDENCE_THRESHOLD else 'Possibly Adult'
        elif label == 'violent':
            return 'Violent / Gore' if confidence >= _CONFIDENCE_THRESHOLD else 'Possibly Violent'
        elif label == 'disturbing':
            return 'Disturbing' if confidence >= _CONFIDENCE_THRESHOLD else 'Possibly Disturbing'
        return 'Unknown'


def _load_image(path):
    """Load and resize an image for CLIP inference. Returns None on failure."""
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((224, 224), Image.BICUBIC)
        return img
    except Exception as e:
        print(f"[WARN] Failed to load image: {path} ({e})")
        return None


def scan_content_batch(image_paths, progress_callback=None, batch_size=32):
    """
    Run CLIP inference on a list of image paths.

    Args:
        image_paths: list of file path strings
        progress_callback: optional callable(current, total, filename)
        batch_size: images per CLIP forward pass

    Returns:
        list of (path, label, confidence, all_scores) tuples.
        Failed images return (path, 'error', 0.0, {}).
    """
    if not image_paths:
        return []

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(_load_image, image_paths))

    failed_paths = {path for img, path in zip(images, image_paths) if img is None}
    valid_pairs = [(img, path) for img, path in zip(images, image_paths) if img is not None]

    if not valid_pairs:
        return [(path, 'error', 0.0, {}) for path in image_paths]

    valid_images, valid_paths = zip(*valid_pairs)

    # Build text prompt list and owner index
    texts, owners = [], []
    for lbl, prompts in LABELS.items():
        for p in prompts:
            texts.append(p)
            owners.append(lbl)
    owners_np = np.array(owners)

    load_models()

    all_results = {}
    total_valid = len(valid_images)

    for batch_start in range(0, total_valid, batch_size):
        batch_imgs = list(valid_images[batch_start:batch_start + batch_size])
        batch_paths = list(valid_paths[batch_start:batch_start + batch_size])

        inputs = processor(text=texts, images=batch_imgs, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.inference_mode(), torch.autocast(
                device_type="cuda", dtype=torch.float16, enabled=(device == "cuda")):
            out = model(**inputs).logits_per_image  # [batch, num_prompts]
            probs = out.softmax(dim=-1).float().cpu().numpy()

        for prob, path in zip(probs, batch_paths):
            scores = {lbl: float(prob[owners_np == lbl].sum()) for lbl in LABELS}
            pred = max(scores, key=scores.get)
            all_results[path] = (pred, scores[pred], scores)

        if progress_callback:
            progress_callback(batch_start + len(batch_imgs), total_valid, "")

    # Reconstruct in original order
    output = []
    for path in image_paths:
        if path in failed_paths:
            output.append((path, 'error', 0.0, {}))
        else:
            pred, conf, scores = all_results[path]
            output.append((path, pred, conf, scores))
    return output


def scan_folder_safe_content(folder_path, progress_callback=None):
    """
    Scan all images in a folder for inappropriate content.

    Args:
        folder_path: path to the folder to scan
        progress_callback: optional callable(current, total, filename)

    Returns:
        dict with keys:
            'safe_images':       [(path, confidence, all_scores), ...]  sorted desc by confidence
            'adult_images':      [(path, confidence, all_scores), ...]  sorted desc by confidence
            'violent_images':    [(path, confidence, all_scores), ...]  sorted desc by confidence
            'disturbing_images': [(path, confidence, all_scores), ...]  sorted desc by confidence
            'error_images':      [path, ...]
            'total_processed':   int
            'total_flagged':     int  (adult + violent + disturbing)
    """
    folder = Path(folder_path)
    image_paths = [
        str(p) for p in folder.rglob('*')
        if p.suffix.lower() in IMG_EXT and 'Trash' not in p.parts
    ]

    result = {
        'safe_images': [],
        'adult_images': [],
        'violent_images': [],
        'disturbing_images': [],
        'error_images': [],
        'total_processed': 0,
        'total_flagged': 0,
    }

    if not image_paths:
        return result

    total = len(image_paths)

    def _progress(current, _total_valid, filename):
        if progress_callback:
            progress_callback(current, total, filename)

    batch_results = scan_content_batch(image_paths, _progress)

    for path, label, confidence, all_scores in batch_results:
        if label == 'error':
            result['error_images'].append(path)
        elif label == 'safe':
            result['safe_images'].append((path, confidence, all_scores))
        elif label == 'adult':
            result['adult_images'].append((path, confidence, all_scores))
        elif label == 'violent':
            result['violent_images'].append((path, confidence, all_scores))
        elif label == 'disturbing':
            result['disturbing_images'].append((path, confidence, all_scores))

    # Sort flagged categories descending by confidence (most concerning first)
    for key in ('adult_images', 'violent_images', 'disturbing_images', 'safe_images'):
        result[key].sort(key=lambda x: x[1], reverse=True)

    result['total_processed'] = len(batch_results)
    result['total_flagged'] = (
        len(result['adult_images']) +
        len(result['violent_images']) +
        len(result['disturbing_images'])
    )

    return result
