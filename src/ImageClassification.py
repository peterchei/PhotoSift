import os, glob, time, sys
from pathlib import Path

import torch, numpy as np
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

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

try:
    model_path = get_model_path()
    model = CLIPModel.from_pretrained(model_path).to(device).eval()
    processor = CLIPProcessor.from_pretrained(model_path)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    print(f"Attempted to load from: {model_path}")
    raise

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
    return classify_people_vs_screenshot_batch([path])[0]


def _load_image(path):
    from PIL import Image
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((224, 224), Image.BICUBIC)
        return img
    except Exception as e:
        print(f"[WARN] Failed to load image: {path} ({e})")
        return None

def classify_people_vs_screenshot_batch(paths):
    # Parallel image loading
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(_load_image, paths))
    # Filter out failed images (None)
    valid = [(img, path) for img, path in zip(images, paths) if img is not None]
    if not valid:
        return []
    images, valid_paths = zip(*valid)
    texts, owners = [], []
    for lbl, prompts in LABELS.items():
        for p in prompts:
            texts.append(p)
            owners.append(lbl)
    inputs = processor(text=texts, images=list(images), return_tensors="pt", padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.inference_mode(), torch.autocast(device_type="cuda", dtype=torch.float16, enabled=(device=="cuda")):
        out = model(**inputs).logits_per_image  # [batch, num_prompts]
        probs = out.softmax(dim=-1).float().cpu().numpy()  # [batch, num_prompts]
    owners = np.array(owners)
    results = []
    for prob in probs:
        scores = {lbl: float(prob[owners == lbl].sum()) for lbl in LABELS}
        pred = max(scores, key=scores.get)
        results.append((pred, scores[pred], scores))
    # Map results back to original paths, fill skipped with None
    out_results = []
    valid_iter = iter(results)
    for img, path in zip(images, valid_paths):
        out_results.append(next(valid_iter))
    # For skipped images, return None
    final_results = []
    valid_idx = 0
    for orig_path in paths:
        if valid_idx < len(valid_paths) and orig_path == valid_paths[valid_idx]:
            final_results.append(out_results[valid_idx])
            valid_idx += 1
        else:
            final_results.append(None)
    return final_results




IMG_EXT = {".jpg",".jpeg",".png"}
def classify_folder(folder: str):
    t0 = time.perf_counter()
    files = [p for p in glob.glob(os.path.join(folder, "**", "*"), recursive=True)
             if Path(p).suffix.lower() in IMG_EXT]
    for p in files:
        label, conf, _ = classify_people_vs_screenshot(p)
        print(f"{p} -> {label} ({conf:.3f})")
    print(f"Done {len(files)} images in {time.perf_counter()-t0:.2f}s")


if __name__ == "__main__":
    print(classify_folder("test_images"))
