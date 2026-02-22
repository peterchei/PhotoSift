"""
Low Resolution Image Detection Module
Detects images below a minimum pixel dimension threshold using PIL metadata.
"""

import os
import multiprocessing
from PIL import Image
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


class LowResolutionDetector:
    def __init__(self, min_width=1280, min_height=720):
        self.min_width = min_width
        self.min_height = min_height

    def get_dimensions(self, image_path):
        """Return (width, height) or (-1, -1) on failure."""
        try:
            with Image.open(str(image_path)) as img:
                return img.size  # (width, height)
        except Exception as e:
            print(f"Error reading {image_path}: {e}")
            return (-1, -1)

    def is_low_res(self, image_path):
        """Return (is_low_res: bool, width: int, height: int)."""
        width, height = self.get_dimensions(image_path)
        if width == -1:
            return (False, -1, -1)  # cannot process, don't flag
        return (width < self.min_width or height < self.min_height, width, height)

    def get_resolution_quality(self, width, height):
        """Categorize resolution quality based on shorter side."""
        if width == -1 or height == -1:
            return "Unknown"
        short = min(width, height)
        if short < 240:   return "Tiny"
        if short < 480:   return "Low"
        if short < 720:   return "SD"
        if short < 1080:  return "HD"
        if short < 1440:  return "Full HD"
        if short < 2160:  return "High Res"
        return "Ultra HD"


def detect_low_res_images_batch(folder_path, min_width=1280, min_height=720,
                                 progress_callback=None, max_workers=None):
    """
    Scan folder for images below the minimum dimensions.

    Returns:
        dict: {
            'low_res_images': [(path, width, height), ...],   # sorted smallest first
            'ok_images':      [(path, width, height), ...],
            'total_processed': int,
            'total_low_res':   int,
        }
    """
    detector = LowResolutionDetector(min_width=min_width, min_height=min_height)
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}

    image_files = []
    for ext in image_extensions:
        for img_path in Path(folder_path).rglob(f'*{ext}'):
            if 'Trash' not in img_path.parts:
                image_files.append(img_path)
        for img_path in Path(folder_path).rglob(f'*{ext.upper()}'):
            if 'Trash' not in img_path.parts:
                image_files.append(img_path)
    image_files = list(set(image_files))  # deduplicate

    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 8)

    low_res_images = []
    ok_images = []
    total = len(image_files)
    processed = 0

    def process_single(img_path):
        flag, w, h = detector.is_low_res(str(img_path))
        return (str(img_path), w, h, flag)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single, p): p for p in image_files}
        for future in as_completed(futures):
            img_path = futures[future]
            try:
                path_str, w, h, flag = future.result()
                if w != -1:
                    if flag:
                        low_res_images.append((path_str, w, h))
                    else:
                        ok_images.append((path_str, w, h))
                processed += 1
                if progress_callback:
                    progress_callback(processed, total, img_path.name)
            except Exception as e:
                print(f"Error: {e}")
                processed += 1

    # Sort: low-res ascending by short side (worst first); ok descending
    low_res_images.sort(key=lambda x: min(x[1], x[2]))
    ok_images.sort(key=lambda x: min(x[1], x[2]), reverse=True)

    return {
        'low_res_images': low_res_images,
        'ok_images': ok_images,
        'total_processed': len(low_res_images) + len(ok_images),
        'total_low_res': len(low_res_images),
    }


def get_recommended_thresholds():
    return {
        'minimal': {'value_w': 640,  'value_h': 480,  'label': '480p',     'description': 'Flag only tiny images (below 640x480)'},
        'normal':  {'value_w': 1280, 'value_h': 720,  'label': '720p HD',  'description': 'Flag images below 1280x720 (recommended)'},
        'strict':  {'value_w': 1920, 'value_h': 1080, 'label': '1080p FHD','description': 'Flag images below 1920x1080 Full HD'},
    }
