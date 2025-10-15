"""
Microsoft Store Asset Generator for PhotoSift
Creates all required logo assets with proper transparency and scaling
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_store_assets():
    """
    Generate all required Microsoft Store assets with proper formats
    
    Microsoft Store Requirements:
    - Square44x44Logo: 44x44px (App list icon - REQUIRED)
    - Square150x150Logo: 150x150px (Medium tile - REQUIRED)
    - StoreLogo: 50x50px (Store listing - OPTIONAL but recommended)
    - All PNGs must support transparency (RGBA mode)
    - Icons should have clear padding and visibility on any background
    """
    
    # Ensure store assets directory exists
    assets_dir = os.path.join("store_package", "Assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    print("=" * 60)
    print("Creating Microsoft Store Assets for PhotoSift v1.3.1")
    print("=" * 60)
    print()

    # Try to load the existing icon
    icon_path = os.path.join("resources", "app.ico")
    source_icon = None
    
    try:
        source_icon = Image.open(icon_path)
        print(f"✓ Loaded source icon: {icon_path}")
        print(f"  - Mode: {source_icon.mode}, Size: {source_icon.size}")
    except Exception as e:
        print(f"⚠ Warning: Could not load app.ico: {e}")
        print("  Creating fallback icons with PhotoSift branding...")

    # Define required sizes per Microsoft Store requirements
    # Format: (name, size, description)
    required_assets = [
        ("Square44x44Logo", 44, "App list icon (REQUIRED)"),
        ("Square150x150Logo", 150, "Medium tile (REQUIRED)"),
        ("StoreLogo", 50, "Store listing logo (RECOMMENDED)"),
    ]
    
    # Optional additional sizes that may be needed
    optional_assets = [
        ("Square71x71Logo", 71, "Small tile (OPTIONAL)"),
        ("Square310x310Logo", 310, "Large tile (OPTIONAL)"),
    ]

    print()
    print("Creating required assets:")
    print("-" * 60)
    
    # Create each required asset
    for name, size, description in required_assets:
        create_logo_asset(source_icon, assets_dir, name, size, description, required=True)
    
    print()
    print("Creating optional assets:")
    print("-" * 60)
    
    # Create optional assets
    for name, size, description in optional_assets:
        create_logo_asset(source_icon, assets_dir, name, size, description, required=False)
    
    print()
    print("=" * 60)
    print("✓ All Microsoft Store assets created successfully!")
    print("=" * 60)
    print()
    print("Asset Location: store_package/Assets/")
    print()
    print("Next Steps:")
    print("1. Review assets in store_package/Assets/ folder")
    print("2. Run create_store_package.bat to build MSIX package")
    print("3. Upload PhotoSift.msix to Microsoft Partner Center")
    print()

def create_logo_asset(source_icon, assets_dir, name, size, description, required=True):
    """
    Create a single logo asset with proper transparency and scaling
    
    Args:
        source_icon: Source PIL Image object (or None for fallback)
        assets_dir: Output directory path
        name: Asset filename (without extension)
        size: Target size in pixels (square)
        description: Human-readable description
        required: Whether this asset is required by Microsoft Store
    """
    try:
        output_path = os.path.join(assets_dir, f"{name}.png")
        
        if source_icon:
            # Use existing icon with proper transparency handling
            # Create new RGBA image
            logo = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Resize source icon maintaining aspect ratio
            # Add 10% padding for better visibility
            padding = int(size * 0.1)
            target_size = size - (padding * 2)
            
            # Convert source to RGBA if needed
            if source_icon.mode != 'RGBA':
                icon_rgba = source_icon.convert('RGBA')
            else:
                icon_rgba = source_icon.copy()
            
            # Resize with high-quality resampling
            icon_resized = icon_rgba.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Center the icon on transparent background
            position = ((size - target_size) // 2, (size - target_size) // 2)
            logo.paste(icon_resized, position, icon_resized)
            
        else:
            # Create fallback icon with PhotoSift branding
            logo = create_fallback_logo(size)
        
        # Save as PNG with transparency
        logo.save(output_path, "PNG", optimize=True)
        
        # Get file size for reporting
        file_size = os.path.getsize(output_path)
        file_size_kb = file_size / 1024
        
        status = "REQUIRED" if required else "OPTIONAL"
        print(f"✓ {name}.png ({size}x{size}px) - {description}")
        print(f"  [{status}] Size: {file_size_kb:.1f} KB - {output_path}")
        
    except Exception as e:
        print(f"✗ Error creating {name}.png: {e}")
        if required:
            print(f"  WARNING: This is a REQUIRED asset for Microsoft Store!")

def create_fallback_logo(size):
    """
    Create a fallback logo with PhotoSift branding when source icon is unavailable
    
    Args:
        size: Target size in pixels (square)
    
    Returns:
        PIL Image object with RGBA mode
    """
    # Create base image with gradient
    logo = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    
    # Draw gradient background circle
    padding = size // 8
    circle_bbox = [padding, padding, size - padding, size - padding]
    
    # Modern blue gradient colors
    color1 = (59, 130, 246, 255)  # Blue-500
    color2 = (37, 99, 235, 255)   # Blue-600
    
    # Draw filled circle
    draw.ellipse(circle_bbox, fill=color1, outline=color2, width=max(2, size // 30))
    
    # Draw simplified camera icon in center
    icon_size = size // 2
    icon_x = (size - icon_size) // 2
    icon_y = (size - icon_size) // 2
    
    # Camera body
    body_padding = icon_size // 4
    body_bbox = [
        icon_x + body_padding,
        icon_y + body_padding,
        icon_x + icon_size - body_padding,
        icon_y + icon_size - body_padding
    ]
    draw.rounded_rectangle(body_bbox, radius=size//20, fill=(255, 255, 255, 255))
    
    # Camera lens (circle)
    lens_size = icon_size // 3
    lens_x = icon_x + (icon_size - lens_size) // 2
    lens_y = icon_y + (icon_size - lens_size) // 2
    lens_bbox = [lens_x, lens_y, lens_x + lens_size, lens_y + lens_size]
    draw.ellipse(lens_bbox, fill=color2, outline=(255, 255, 255, 255), width=max(1, size // 50))
    
    return logo

if __name__ == "__main__":
    create_store_assets()