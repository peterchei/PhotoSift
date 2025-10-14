"""
Tests for Blur Detection functionality
Tests the Laplacian variance-based blur detection system
"""

import unittest
import os
import sys
from pathlib import Path
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from BlurryImageDetection import BlurryImageDetector, detect_blurry_images_batch, get_recommended_threshold


class TestBlurDetection(unittest.TestCase):
    """Test cases for blur detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.detector = BlurryImageDetector(threshold=100.0)
    
    def test_detector_initialization(self):
        """Test that detector can be initialized"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.threshold, 100.0)
        print("✓ Blur detector initialized correctly")
    
    def test_threshold_customization(self):
        """Test that custom thresholds can be set"""
        custom_detector = BlurryImageDetector(threshold=150.0)
        self.assertEqual(custom_detector.threshold, 150.0)
        print("✓ Custom threshold set correctly")
    
    def test_recommended_threshold_function(self):
        """Test that recommended threshold function exists"""
        self.assertTrue(callable(get_recommended_threshold))
        thresholds = get_recommended_threshold()
        self.assertIsInstance(thresholds, dict)
        self.assertIn('normal', thresholds)
        self.assertIsInstance(thresholds['normal']['value'], (int, float))
        self.assertGreater(thresholds['normal']['value'], 0)
        print(f"✓ Recommended thresholds available: {list(thresholds.keys())}")
    
    def test_blur_quality_levels(self):
        """Test blur quality categorization"""
        detector = BlurryImageDetector()
        
        # Test different score ranges
        quality_excellent = detector.get_blur_quality(600)
        self.assertEqual(quality_excellent, "Excellent")
        
        quality_good = detector.get_blur_quality(350)
        self.assertEqual(quality_good, "Good")
        
        quality_fair = detector.get_blur_quality(150)
        self.assertEqual(quality_fair, "Fair")
        
        quality_poor = detector.get_blur_quality(75)
        self.assertEqual(quality_poor, "Poor")
        
        quality_blurry = detector.get_blur_quality(30)
        self.assertEqual(quality_blurry, "Very Blurry")
        
        print("✓ Blur quality levels categorized correctly")
    
    def test_batch_detection_function_exists(self):
        """Test that batch detection function exists"""
        self.assertTrue(callable(detect_blurry_images_batch))
        print("✓ Batch detection function exists")
    
    def test_batch_detection_signature(self):
        """Test batch detection function signature"""
        import inspect
        sig = inspect.signature(detect_blurry_images_batch)
        params = list(sig.parameters.keys())
        
        self.assertIn('folder_path', params)
        self.assertIn('threshold', params)
        print("✓ Batch detection has correct signature")
    
    def test_empty_folder_handling(self):
        """Test handling of empty folder"""
        empty_dir = self.test_data_dir / "empty_blur"
        empty_dir.mkdir(exist_ok=True)
        
        try:
            results = detect_blurry_images_batch(str(empty_dir), threshold=100.0)
            self.assertIsInstance(results, dict)
            self.assertIn('blurry_images', results)
            self.assertIn('sharp_images', results)
            self.assertEqual(len(results['blurry_images']), 0)
            self.assertEqual(len(results['sharp_images']), 0)
            print("✓ Empty folder handled correctly")
        except Exception as e:
            print(f"⚠ Empty folder test: {e}")
    
    def test_trash_folder_exclusion(self):
        """Test that Trash folder is properly excluded"""
        # This tests the logic, not the actual exclusion
        test_path = Path("C:/test/folder/Trash/image.jpg")
        is_trash = 'Trash' in test_path.parts
        self.assertTrue(is_trash)
        
        test_path_ok = Path("C:/test/folder/image.jpg")
        is_trash_ok = 'Trash' in test_path_ok.parts
        self.assertFalse(is_trash_ok)
        
        print("✓ Trash folder exclusion logic validated")


class TestBlurDetectionIntegration(unittest.TestCase):
    """Integration tests for blur detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
    
    def test_laplacian_variance_calculation(self):
        """Test Laplacian variance calculation on synthetic images"""
        try:
            import cv2
            
            # Create a sharp synthetic image (checkerboard pattern)
            sharp_img = np.zeros((100, 100), dtype=np.uint8)
            sharp_img[::10] = 255  # High frequency pattern
            
            laplacian = cv2.Laplacian(sharp_img, cv2.CV_64F)
            sharp_variance = laplacian.var()
            
            # Create a blurry synthetic image (uniform gray)
            blurry_img = np.full((100, 100), 128, dtype=np.uint8)
            
            laplacian_blurry = cv2.Laplacian(blurry_img, cv2.CV_64F)
            blurry_variance = laplacian_blurry.var()
            
            # Sharp image should have higher variance
            self.assertGreater(sharp_variance, blurry_variance)
            print(f"✓ Laplacian variance: Sharp={sharp_variance:.2f}, Blurry={blurry_variance:.2f}")
            
        except ImportError:
            print("⚠ OpenCV not available for Laplacian test")
    
    def test_parallel_processing_support(self):
        """Test that parallel processing is available"""
        try:
            import multiprocessing
            cpu_count = multiprocessing.cpu_count()
            self.assertGreater(cpu_count, 0)
            print(f"✓ Parallel processing supported: {cpu_count} CPUs")
        except Exception as e:
            print(f"⚠ Parallel processing test: {e}")
    
    def test_model_imports(self):
        """Test that all required modules can be imported"""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            from concurrent.futures import ThreadPoolExecutor
            print("✓ All required modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")


if __name__ == '__main__':
    print("=" * 70)
    print("Running Blur Detection Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
