import os
import shutil
from transformers import CLIPModel, CLIPProcessor

def download_model():
    print("Downloading CLIP model files...")
    model_id = "openai/clip-vit-base-patch32"
    local_model_path = os.path.join("models", "clip-vit-base-patch32")
    
    # Create models directory if it doesn't exist
    os.makedirs(local_model_path, exist_ok=True)
    
    # Download model and processor
    model = CLIPModel.from_pretrained(model_id)
    processor = CLIPProcessor.from_pretrained(model_id)
    
    # Save them locally
    model.save_pretrained(local_model_path)
    processor.save_pretrained(local_model_path)
    
    print(f"Model files downloaded to {local_model_path}")

if __name__ == "__main__":
    download_model()