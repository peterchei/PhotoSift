"""
Blurry Image Detection Module
Detects blurry/out-of-focus images using Laplacian variance method
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing


class BlurryImageDetector:
    """
    Detects blurry images using the Laplacian variance method.
    
    The Laplacian operator calculates the second derivative of an image,
    measuring the rate of change of pixel intensities. Sharp images have
    high variance in the Laplacian, while blurry images have low variance.
    """
    
    def __init__(self, threshold=100.0):
        """
        Initialize the blur detector.
        
        Args:
            threshold (float): Variance threshold below which an image is considered blurry.
                             Default: 100.0
                             - Lower values (50-100): More strict, flags more images as blurry
                             - Higher values (150-200): More lenient, only very blurry images flagged
        """
        self.threshold = threshold
        
    def calculate_blur_score(self, image_path):
        """
        Calculate the blur score (Laplacian variance) for an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            float: Blur score (higher = sharper, lower = blurrier)
                   Returns -1 if image cannot be processed
        """
        try:
            # Read image
            image = cv2.imread(str(image_path))
            if image is None:
                # Try with PIL if cv2 fails
                pil_image = Image.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            return variance
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return -1
    
    def is_blurry(self, image_path):
        """
        Determine if an image is blurry.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (is_blurry: bool, blur_score: float)
        """
        score = self.calculate_blur_score(image_path)
        
        if score == -1:
            return (False, score)  # Unable to process, assume not blurry
        
        return (score < self.threshold, score)
    
    def get_blur_quality(self, blur_score):
        """
        Categorize image quality based on blur score.
        
        Args:
            blur_score (float): The calculated blur score
            
        Returns:
            str: Quality category ("Excellent", "Good", "Fair", "Poor", "Very Blurry", "Unknown")
        """
        if blur_score == -1:
            return "Unknown"
        elif blur_score > 500:
            return "Excellent"
        elif blur_score > 250:
            return "Good"
        elif blur_score > 100:
            return "Fair"
        elif blur_score > 50:
            return "Poor"
        else:
            return "Very Blurry"


def detect_blurry_images_batch(folder_path, threshold=100.0, progress_callback=None, batch_size=10, max_workers=None):
    """
    Scan a folder for blurry images using parallel batch processing for better performance.
    
    Args:
        folder_path (str): Path to the folder containing images
        threshold (float): Blur detection threshold
        progress_callback (callable): Optional callback function(current, total, filename)
        batch_size (int): Number of images to process in each batch
        max_workers (int): Maximum number of parallel workers (default: CPU count)
        
    Returns:
        dict: {
            'blurry_images': [(path, score), ...],
            'sharp_images': [(path, score), ...],
            'total_processed': int,
            'total_blurry': int
        }
    """
    detector = BlurryImageDetector(threshold=threshold)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Find all images
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(folder_path).rglob(f'*{ext}'))
        image_files.extend(Path(folder_path).rglob(f'*{ext.upper()}'))
    
    blurry_images = []
    sharp_images = []
    total = len(image_files)
    processed = 0
    
    # Use CPU count if max_workers not specified
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 8)  # Cap at 8 to avoid overhead
    
    def process_single_image(image_path):
        """Process a single image and return result"""
        try:
            is_blurry, score = detector.is_blurry(str(image_path))
            return (str(image_path), score, is_blurry)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return (str(image_path), -1, False)
    
    # Process images in parallel batches
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {executor.submit(process_single_image, img_path): img_path 
                         for img_path in image_files}
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_path):
            img_path = future_to_path[future]
            try:
                path_str, score, is_blurry = future.result()
                
                if score != -1:  # Successfully processed
                    if is_blurry:
                        blurry_images.append((path_str, score))
                    else:
                        sharp_images.append((path_str, score))
                
                processed += 1
                
                # Update progress
                if progress_callback:
                    progress_callback(processed, total, img_path.name)
                    
            except Exception as e:
                print(f"Error processing result for {img_path}: {e}")
                processed += 1
    
    # Sort by blur score (most blurry first for blurry_images, sharpest first for sharp_images)
    blurry_images.sort(key=lambda x: x[1])  # Lowest score (most blurry) first
    sharp_images.sort(key=lambda x: x[1], reverse=True)  # Highest score (sharpest) first
    
    return {
        'blurry_images': blurry_images,
        'sharp_images': sharp_images,
        'total_processed': len(blurry_images) + len(sharp_images),
        'total_blurry': len(blurry_images)
    }


def detect_blurry_images(folder_path, threshold=100.0, progress_callback=None):
    """
    Scan a folder for blurry images.
    
    Args:
        folder_path (str): Path to the folder containing images
        threshold (float): Blur detection threshold
        progress_callback (callable): Optional callback function(current, total, filename)
        
    Returns:
        dict: {
            'blurry_images': [(path, score), ...],
            'sharp_images': [(path, score), ...],
            'total_processed': int,
            'total_blurry': int
        }
    """
    detector = BlurryImageDetector(threshold=threshold)
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Find all images
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(folder_path).rglob(f'*{ext}'))
        image_files.extend(Path(folder_path).rglob(f'*{ext.upper()}'))
    
    blurry_images = []
    sharp_images = []
    total = len(image_files)
    
    for idx, image_path in enumerate(image_files, 1):
        if progress_callback:
            progress_callback(idx, total, image_path.name)
        
        is_blurry, score = detector.is_blurry(str(image_path))
        
        if score != -1:  # Successfully processed
            if is_blurry:
                blurry_images.append((str(image_path), score))
            else:
                sharp_images.append((str(image_path), score))
    
    # Sort by blur score (most blurry first for blurry_images, sharpest first for sharp_images)
    blurry_images.sort(key=lambda x: x[1])  # Lowest score (most blurry) first
    sharp_images.sort(key=lambda x: x[1], reverse=True)  # Highest score (sharpest) first
    
    return {
        'blurry_images': blurry_images,
        'sharp_images': sharp_images,
        'total_processed': len(blurry_images) + len(sharp_images),
        'total_blurry': len(blurry_images)
    }


def get_recommended_threshold():
    """
    Get recommended threshold values with descriptions.
    
    Returns:
        dict: Threshold presets with descriptions
    """
    return {
        'very_strict': {
            'value': 200.0,
            'description': 'Very Strict - Only perfectly sharp images pass'
        },
        'strict': {
            'value': 150.0,
            'description': 'Strict - High quality standards'
        },
        'normal': {
            'value': 100.0,
            'description': 'Normal - Balanced detection (recommended)'
        },
        'lenient': {
            'value': 50.0,
            'description': 'Lenient - Only very blurry images flagged'
        },
        'very_lenient': {
            'value': 25.0,
            'description': 'Very Lenient - Only extremely blurry images'
        }
    }


if __name__ == "__main__":
    # Test the detector
    import sys
    
    if len(sys.argv) > 1:
        test_folder = sys.argv[1]
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
        
        print(f"Scanning folder: {test_folder}")
        print(f"Threshold: {threshold}")
        print("=" * 60)
        
        def progress(current, total, filename):
            print(f"Processing {current}/{total}: {filename}")
        
        results = detect_blurry_images(test_folder, threshold, progress)
        
        print("=" * 60)
        print(f"Total processed: {results['total_processed']}")
        print(f"Blurry images: {results['total_blurry']}")
        print(f"Sharp images: {len(results['sharp_images'])}")
        
        if results['blurry_images']:
            print("\nTop 5 blurriest images:")
            for path, score in results['blurry_images'][:5]:
                print(f"  {os.path.basename(path)}: {score:.2f}")
    else:
        print("Usage: python BlurryImageDetection.py <folder_path> [threshold]")
        print("\nRecommended thresholds:")
        for name, info in get_recommended_threshold().items():
            print(f"  {info['value']}: {info['description']}")
