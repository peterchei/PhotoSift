# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# pip install transformers pillow

#pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

# 1) Load model & processor (first run downloads weights)
device = "cuda" if torch.cuda.is_available() else "cpu"
#device = "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# 2) Define your two classes with a few prompt variants (helps zero-shot)
LABELS = {
    "people": [
        "a photo of a person",
        "a photo of people",
        "a portrait photo",
        "a candid photo of a person"
    ],
    "screenshot": [
        "a computer screenshot",
        "a mobile phone screenshot",
        "a screen capture of an app UI",
        "a screenshot of a website"
    ]
}

def classify_people_vs_screenshot(image_path: str):
    image = Image.open(image_path).convert("RGB")

    # Flatten text prompts and remember which label they belong to
    texts, owners = [], []
    for label, prompts in LABELS.items():
        for p in prompts:
            texts.append(p)
            owners.append(label)

    # 3) Preprocess and run CLIP
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        # CLIP returns similarity logits between image and each text prompt
        logits = outputs.logits_per_image.squeeze(0)  # shape [num_prompts]
        probs = logits.softmax(dim=0).cpu()

    # 4) Aggregate prompt probabilities per label
    import numpy as np
    probs_np = probs.numpy()
    owners_np = np.array(owners)
    result = {}
    for lbl in LABELS:
        result[lbl] = float(probs_np[owners_np == lbl].sum())

    # 5) Pick the winner and provide a confidence
    winner = max(result, key=result.get)
    confidence = result[winner]
    return winner, confidence, result

if __name__ == "__main__":
    path = ".\\test_image\\2.jpg"  # <-- replace with your image file
    label, conf, full = classify_people_vs_screenshot(path)
    print(f"Prediction: {label}  | confidence: {conf:.3f}")
    print("class probabilities:", full)
    label, conf, full = classify_people_vs_screenshot(".\\test_image\\test_image.jpg")
    print(f"Prediction: {label}  | confidence: {conf:.3f}")
    print("class probabilities:", full)
