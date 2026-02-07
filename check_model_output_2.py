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

print("\nTesting model.get_image_features(...)")
# Pass only image-related inputs
image_inputs = {k: v for k, v in inputs.items() if k in ['pixel_values']}
features = model.get_image_features(**image_inputs)
print(f"Type of features: {type(features)}")
if torch.is_tensor(features):
    print("Features is a Tensor")
else:
    print(f"Features attributes: {dir(features)}")
