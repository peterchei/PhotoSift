import os, sys
import torch
from transformers import CLIPModel, CLIPProcessor
from PIL import Image

device = "cpu"
model_path = os.path.join('/home/peterchei/projects/PhotoSift/models', 'clip-vit-base-patch32')
if not os.path.exists(model_path):
    model_path = "openai/clip-vit-base-patch32"

print(f"Loading model from {model_path}...")
model = CLIPModel.from_pretrained(model_path).to(device)
processor = CLIPProcessor.from_pretrained(model_path)

# Create a dummy image
img = Image.new('RGB', (224, 224), color = (73, 109, 137))
inputs = processor(images=img, return_tensors="pt")

print("Testing model(**inputs)...")
outputs = model(**inputs)
print(f"Type of outputs: {type(outputs)}")
if hasattr(outputs, 'logits_per_image'):
    print(f"Type of logits_per_image: {type(outputs.logits_per_image)}")
else:
    print("logits_per_image not found in outputs")

print("\nTesting model.get_image_features(...)")
features = model.get_image_features(**inputs)
print(f"Type of features: {type(features)}")
