from PIL import Image
import os

def create_store_assets():
    # Ensure store assets directory exists
    assets_dir = os.path.join("store_package", "Assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Load the icon
    try:
        icon = Image.open(os.path.join("resources", "app.ico"))
    except:
        print("Error: Could not find app.ico in resources directory")
        return

    # Define required sizes for store assets
    sizes = {
        "StoreLogo": 50,
        "Square44x44Logo": 44,
        "Square71x71Logo": 71,
        "Square150x150Logo": 150,
        "Square310x310Logo": 310
    }

    # Create each required size
    for name, size in sizes.items():
        resized = icon.resize((size, size), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (PNG with alpha channel)
        if resized.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', resized.size, (255, 255, 255))
            background.paste(resized, mask=resized.split()[-1])
            resized = background

        output_path = os.path.join(assets_dir, f"{name}.png")
        resized.save(output_path, "PNG")
        print(f"Created {output_path}")

if __name__ == "__main__":
    create_store_assets()