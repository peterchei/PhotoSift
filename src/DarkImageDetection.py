"""
Dark Image Detection Module
Detects dark/underexposed images using HSV Value channel analysis
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing


class DarkImageDetector:
    """
    Detects dark/underexposed images.
    
    Uses HSV color space to analyze the Value (brightness) channel.
    Lower average brightness indicates darker images.
    """
    
    def __init__(self, threshold=40.0):
        """
        Initialize the dark detector.
        
        Args:
            threshold (float): Brightness threshold below which an image is considered dark.
                             Range 0-255.
                             Default: 40.0
        """
        self.threshold = threshold
        
    def calculate_brightness_score(self, image_path):
        """
        Calculate the brightness score (average Value in HSV) for an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            float: Brightness score (0-255, higher = brighter)
                   Returns -1 if image cannot be processed
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                # Try with PIL if cv2 fails
                pil_image = Image.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to HSV color space
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Extract Value channel
            v_channel = hsv[:, :, 2]
            
            # Calculate average brightness
            avg_brightness = np.mean(v_channel)
            
            return avg_brightness
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return -1
    
    def is_dark(self, image_path):
        """
        Determine if an image is too dark.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (is_dark: bool, brightness_score: float)
        """
        score = self.calculate_brightness_score(image_path)
        
        if score == -1:
            return (False, score)  # Unable to process, assume not dark
        
        return (score < self.threshold, score)
    
    def get_brightness_quality(self, brightness_score):
        """
        Categorize image quality based on brightness score.
        
        Args:
            brightness_score (float): The calculated brightness score (0-255)
            
        Returns:
            str: Quality category
        """
        if brightness_score == -1:
            return "Unknown"
        elif brightness_score < 20:
            return "Very Dark"
        elif brightness_score < 40:
            return "Dark"
        elif brightness_score < 80:
            return "Dim"
        elif brightness_score < 180:
            return "Good"
        elif brightness_score < 220:
            return "Bright"
        else:
            return "Very Bright"


def detect_dark_images_batch(folder_path, threshold=40.0, progress_callback=None, max_workers=None):
    """
    Scan a folder for dark images using parallel batch processing.
    
    Args:
        folder_path (str): Path to the folder containing images
        threshold (float): Dark detection threshold
        progress_callback (callable): Optional callback function(current, total, filename)
        max_workers (int): Maximum number of parallel workers
        
    Returns:
        dict: {
            'dark_images': [(path, score), ...],
            'bright_images': [(path, score), ...],
            'total_processed': int,
            'total_dark': int
        }
    """
    detector = DarkImageDetector(threshold=threshold)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Find all images, excluding Trash folder
    image_files_set = set()
    for ext in image_extensions:
        for img_path in Path(folder_path).rglob(f'*{ext}'):
            if 'Trash' not in img_path.parts:
                image_files_set.add(img_path)
        for img_path in Path(folder_path).rglob(f'*{ext.upper()}'):
            if 'Trash' not in img_path.parts:
                image_files_set.add(img_path)
    
    image_files = list(image_files_set)
    dark_images = []
    bright_images = []
    total = len(image_files)
    processed = 0
    
    # Use CPU count if max_workers not specified
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 8)
    
    def process_single_image(image_path):
        """Process a single image and return result"""
        try:
            is_dark, score = detector.is_dark(str(image_path))
            return (str(image_path), score, is_dark)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return (str(image_path), -1, False)
    
    # Process images in parallel batches
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(process_single_image, img_path): img_path 
                         for img_path in image_files}
        
        for future in as_completed(future_to_path):
            img_path = future_to_path[future]
            try:
                path_str, score, is_dark = future.result()
                
                if score != -1:
                    if is_dark:
                        dark_images.append((path_str, score))
                    else:
                        bright_images.append((path_str, score))
                
                processed += 1
                
                if progress_callback:
                    progress_callback(processed, total, img_path.name)
                    
            except Exception as e:
                print(f"Error processing result for {img_path}: {e}")
                processed += 1
    
    # Sort: dark images (lowest score first), bright images (highest score first)
    dark_images.sort(key=lambda x: x[1])
    bright_images.sort(key=lambda x: x[1], reverse=True)
    
    return {
        'dark_images': dark_images,
        'bright_images': bright_images,
        'total_processed': len(dark_images) + len(bright_images),
        'total_dark': len(dark_images)
    }


def get_recommended_threshold():
    """
    Get recommended threshold values with descriptions.
    """
    return {
        'strict': {
            'value': 20.0,
            'description': 'Strict - Only very dark images flagged'
        },
        'normal': {
            'value': 40.0,
            'description': 'Normal - Balanced detection (recommended)'
        },
        'lenient': {
            'value': 60.0,
            'description': 'Lenient - Flags dimly lit photos too'
        }
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_folder = sys.argv[1]
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 40.0
        
        print(f"Scanning folder: {test_folder}")
        print(f"Threshold: {threshold}")
        print("=" * 60)
        
        def progress(current, total, filename):
            print(f"Processing {current}/{total}: {filename}")
        
        results = detect_dark_images_batch(test_folder, threshold, progress)
        
        print("=" * 60)
        print(f"Total processed: {results['total_processed']}")
        print(f"Dark images: {results['total_dark']}")
        
        if results['dark_images']:
            print("\nTop 5 darkest images:")
            for path, score in results['dark_images'][:5]:
                print(f"  {os.path.basename(path)}: {score:.2f}")
    else:
        print("Usage: python DarkImageDetection.py <folder_path> [threshold]")
