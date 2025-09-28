import os, glob, time
from pathlib import Path

import torch, numpy as np
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device).eval()
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

LABELS = {
    "people": [
        "a photo of a person", "a photo of people",
        "a portrait photo", "a candid photo of a person"
    ],
    "screenshot": [
        "a computer screenshot", "a phone screenshot",
        "a screen capture of an app UI", "a screenshot of a website"
    ],
}


def classify_people_vs_screenshot(path: str):
    # For backward compatibility, single image
    return classify_people_vs_screenshot_batch([path])[0]


def _load_image(path):
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img = img.resize((224, 224), Image.BICUBIC)
    return img

def classify_people_vs_screenshot_batch(paths):
    # Parallel image loading
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        images = list(executor.map(_load_image, paths))
    texts, owners = [], []
    for lbl, prompts in LABELS.items():
        for p in prompts:
            texts.append(p)
            owners.append(lbl)
    inputs = processor(text=texts, images=images, return_tensors="pt", padding=True)
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
    return results




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
