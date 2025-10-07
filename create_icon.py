from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create base image with transparency
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Colors
    primary_color = (51, 153, 255)  # Blue
    secondary_color = (255, 255, 255)  # White
    
    # Draw main circle background
    margin = size // 8
    circle_bbox = (margin, margin, size - margin, size - margin)
    draw.ellipse(circle_bbox, fill=primary_color)
    
    # Draw photo frame symbol
    frame_margin = size // 4
    frame_size = size - (frame_margin * 2)
    frame_bbox = (frame_margin, frame_margin, frame_margin + frame_size, frame_margin + frame_size)
    
    # Draw overlapping rectangles to create photo stack effect
    offset = size // 16
    # Back photo (slightly offset)
    draw.rectangle((frame_margin + offset, frame_margin + offset, 
                   frame_margin + frame_size, frame_margin + frame_size), 
                  fill=(41, 123, 205))  # Darker blue
    
    # Front photo
    draw.rectangle((frame_margin, frame_margin, 
                   frame_margin + frame_size - offset, frame_margin + frame_size - offset), 
                  fill=secondary_color)
    
    # Save in different sizes for the ico file
    sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
    icons = []
    
    for size in sizes:
        resized = image.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Ensure resources directory exists
    os.makedirs('resources', exist_ok=True)
    
    # Save as ICO file
    icons[0].save('resources/app.ico', 
                 format='ICO', 
                 sizes=sizes,
                 append_images=icons[1:])
    
    print("Icon created successfully in resources/app.ico")

if __name__ == '__main__':
    create_icon()