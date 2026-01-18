try:
    from PIL import Image, ImageTk
    print("Successfully imported PIL.Image and PIL.ImageTk")
    img = Image.new('RGB', (10, 10))
    print("Successfully created a new image")
except Exception as e:
    print(f"Failed to import/use PIL: {e}")
