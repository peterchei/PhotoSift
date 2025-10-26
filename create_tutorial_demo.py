#!/usr/bin/env python3
"""
PhotoSift Tutorial Demo Data Generator
Creates sample photo sets for video tutorials
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

def create_sample_image(width, height, text, color, filename):
    """Create a simple sample image with text"""
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill='white', font=font)
    img.save(filename, 'JPEG', quality=85)

def create_blur_variations(base_image_path, output_dir):
    """Create different blur levels of an image"""
    base_img = Image.open(base_image_path)

    # Create different blur levels
    blur_levels = [
        (0, "sharp", (0, 100, 0)),      # Green - excellent
        (1, "slight_blur", (150, 150, 0)), # Yellow - good
        (3, "moderate_blur", (200, 100, 0)), # Orange - fair
        (5, "heavy_blur", (200, 50, 0)),   # Red-orange - poor
        (8, "extreme_blur", (150, 0, 0))   # Red - very blurry
    ]

    for radius, name, color in blur_levels:
        if radius == 0:
            blurred = base_img.copy()
        else:
            blurred = base_img.filter(ImageFilter.GaussianBlur(radius))

        # Add quality indicator
        draw = ImageDraw.Draw(blurred)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()

        quality_text = f"Quality: {name.replace('_', ' ').title()}"
        draw.text((10, 10), quality_text, fill=color, font=font)

        output_path = os.path.join(output_dir, f"sample_{name}.jpg")
        blurred.save(output_path, 'JPEG', quality=85)

def create_duplicate_set(output_dir):
    """Create a set of similar images for duplicate detection demo"""
    base_colors = [
        ('#FF6B6B', 'Red Scene'),
        ('#4ECDC4', 'Blue Scene'),
        ('#45B7D1', 'Teal Scene'),
        ('#96CEB4', 'Green Scene'),
        ('#FFEAA7', 'Yellow Scene')
    ]

    for i, (color, desc) in enumerate(base_colors):
        # Create original
        create_sample_image(800, 600, f"{desc}\nOriginal", color,
                          os.path.join(output_dir, f"original_{i+1}.jpg"))

        # Create slight variation (different size)
        create_sample_image(600, 450, f"{desc}\nResized", color,
                          os.path.join(output_dir, f"resized_{i+1}.jpg"))

        # Create edited version (different color tone)
        color_variation = color.replace('#', '#')
        if i % 2 == 0:
            color_variation = '#8B' + color[3:]  # Darker
        else:
            color_variation = '#FF' + color[3:]  # Lighter

        create_sample_image(800, 600, f"{desc}\nEdited", color_variation,
                          os.path.join(output_dir, f"edited_{i+1}.jpg"))

def create_classification_set(output_dir):
    """Create sample images for classification demo"""
    # People photos
    people_dir = os.path.join(output_dir, 'people')
    os.makedirs(people_dir, exist_ok=True)

    people_scenes = [
        ('#FFB6C1', 'Family Portrait'),
        ('#87CEEB', 'Selfie'),
        ('#DDA0DD', 'Group Photo'),
        ('#F0E68C', 'Pet with Owner')
    ]

    for color, desc in people_scenes:
        create_sample_image(600, 800, f"👨‍👩‍👧‍👦\n{desc}", color,
                          os.path.join(people_dir, f"{desc.lower().replace(' ', '_')}.jpg"))

    # Screenshots
    screenshot_dir = os.path.join(output_dir, 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)

    screenshot_scenes = [
        ('#2C3E50', 'App Screenshot'),
        ('#E74C3C', 'Error Message'),
        ('#3498DB', 'Website Capture'),
        ('#9B59B6', 'Game Screenshot')
    ]

    for color, desc in screenshot_scenes:
        create_sample_image(800, 600, f"🖥️\n{desc}", color,
                          os.path.join(screenshot_dir, f"{desc.lower().replace(' ', '_')}.jpg"))

def main():
    """Generate all demo data for PhotoSift tutorials"""
    print("🎬 Generating PhotoSift Tutorial Demo Data...")

    # Create main demo directory
    demo_dir = "tutorial_demo_photos"
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    os.makedirs(demo_dir)

    # Create duplicate detection samples
    print("📸 Creating duplicate detection samples...")
    dup_dir = os.path.join(demo_dir, "duplicates")
    os.makedirs(dup_dir)
    create_duplicate_set(dup_dir)

    # Create blur detection samples
    print("🌫️ Creating blur detection samples...")
    blur_dir = os.path.join(demo_dir, "blur_examples")
    os.makedirs(blur_dir)

    # Create a base sharp image first
    base_image = os.path.join(blur_dir, "base_sharp.jpg")
    create_sample_image(800, 600, "SHARP PROFESSIONAL PHOTO\nHigh Quality Sample", '#228B22', base_image)

    # Create blur variations
    create_blur_variations(base_image, blur_dir)

    # Create classification samples
    print("🤖 Creating classification samples...")
    class_dir = os.path.join(demo_dir, "classification")
    create_classification_set(class_dir)

    # Create mixed collection for general demos
    print("📂 Creating mixed collection...")
    mixed_dir = os.path.join(demo_dir, "mixed_collection")
    os.makedirs(mixed_dir)

    # Copy samples from each category
    categories = [dup_dir, blur_dir, os.path.join(class_dir, 'people'), os.path.join(class_dir, 'screenshots')]
    for category in categories:
        if os.path.exists(category):
            for file in os.listdir(category)[:3]:  # Take 3 from each category
                src = os.path.join(category, file)
                dst = os.path.join(mixed_dir, f"mixed_{file}")
                shutil.copy2(src, dst)

    print("✅ Demo data generation complete!")
    print(f"📁 Demo photos created in: {demo_dir}")
    print("\n📊 Summary:")
    print(f"   Duplicates: {len(os.listdir(dup_dir))} images")
    print(f"   Blur examples: {len(os.listdir(blur_dir))} images")
    print(f"   People photos: {len(os.listdir(os.path.join(class_dir, 'people')))} images")
    print(f"   Screenshots: {len(os.listdir(os.path.join(class_dir, 'screenshots')))} images")
    print(f"   Mixed collection: {len(os.listdir(mixed_dir))} images")

    print("\n🎬 Ready for recording! Use these folders in your video tutorials.")

if __name__ == "__main__":
    main()