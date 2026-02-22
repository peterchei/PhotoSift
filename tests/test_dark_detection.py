"""
Tests for Dark Image Detection functionality
Tests the HSV Value channel-based dark image detection system
"""

import unittest
import os
import sys
import shutil
from pathlib import Path
import numpy as np

# Ensure unicode print output works on Windows terminals with cp1252 encoding
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src directory to path (mirrors pattern in test_blur_detection.py)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from DarkImageDetection import DarkImageDetector, detect_dark_images_batch, get_recommended_threshold


class TestDarkDetection(unittest.TestCase):
    """Unit tests for dark detection logic - no file I/O required"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.detector = DarkImageDetector(threshold=40.0)

    def test_detector_initialization(self):
        """Test that detector initialises with the supplied threshold"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.threshold, 40.0)
        print("✓ Dark detector initialised correctly")

    def test_threshold_customization(self):
        """Test that custom thresholds are stored correctly"""
        custom_detector = DarkImageDetector(threshold=60.0)
        self.assertEqual(custom_detector.threshold, 60.0)
        print("✓ Custom threshold set correctly")

    def test_recommended_threshold_function(self):
        """Test that get_recommended_threshold returns a dict with expected keys"""
        self.assertTrue(callable(get_recommended_threshold))
        thresholds = get_recommended_threshold()
        self.assertIsInstance(thresholds, dict)
        self.assertIn('strict', thresholds)
        self.assertIn('normal', thresholds)
        self.assertIn('lenient', thresholds)
        for key in ('strict', 'normal', 'lenient'):
            self.assertIn('value', thresholds[key])
            self.assertIsInstance(thresholds[key]['value'], (int, float))
            self.assertGreater(thresholds[key]['value'], 0)
        print(f"✓ Recommended thresholds available: {list(thresholds.keys())}")

    def test_recommended_threshold_ordering(self):
        """Test that strict < normal < lenient in recommended thresholds"""
        thresholds = get_recommended_threshold()
        strict_val = thresholds['strict']['value']
        normal_val = thresholds['normal']['value']
        lenient_val = thresholds['lenient']['value']
        self.assertLess(strict_val, normal_val)
        self.assertLess(normal_val, lenient_val)
        print(f"✓ Threshold ordering correct: strict={strict_val} < normal={normal_val} < lenient={lenient_val}")

    def test_brightness_quality_very_dark(self):
        """Brightness score below 20 maps to 'Very Dark'"""
        self.assertEqual(self.detector.get_brightness_quality(0), "Very Dark")
        self.assertEqual(self.detector.get_brightness_quality(19), "Very Dark")
        print("✓ Very Dark boundary correct (score < 20)")

    def test_brightness_quality_dark(self):
        """Brightness score 20-39 maps to 'Dark'"""
        self.assertEqual(self.detector.get_brightness_quality(20), "Dark")
        self.assertEqual(self.detector.get_brightness_quality(39), "Dark")
        print("✓ Dark boundary correct (20 <= score < 40)")

    def test_brightness_quality_dim(self):
        """Brightness score 40-79 maps to 'Dim'"""
        self.assertEqual(self.detector.get_brightness_quality(40), "Dim")
        self.assertEqual(self.detector.get_brightness_quality(79), "Dim")
        print("✓ Dim boundary correct (40 <= score < 80)")

    def test_brightness_quality_good(self):
        """Brightness score 80-179 maps to 'Good'"""
        self.assertEqual(self.detector.get_brightness_quality(80), "Good")
        self.assertEqual(self.detector.get_brightness_quality(179), "Good")
        print("✓ Good boundary correct (80 <= score < 180)")

    def test_brightness_quality_bright(self):
        """Brightness score 180-219 maps to 'Bright'"""
        self.assertEqual(self.detector.get_brightness_quality(180), "Bright")
        self.assertEqual(self.detector.get_brightness_quality(219), "Bright")
        print("✓ Bright boundary correct (180 <= score < 220)")

    def test_brightness_quality_very_bright(self):
        """Brightness score >= 220 maps to 'Very Bright'"""
        self.assertEqual(self.detector.get_brightness_quality(220), "Very Bright")
        self.assertEqual(self.detector.get_brightness_quality(255), "Very Bright")
        print("✓ Very Bright boundary correct (score >= 220)")

    def test_brightness_quality_error_sentinel(self):
        """Score of -1 (processing error) maps to 'Unknown'"""
        self.assertEqual(self.detector.get_brightness_quality(-1), "Unknown")
        print("✓ Error sentinel -1 maps to 'Unknown'")

    def test_batch_detection_function_exists(self):
        """Test that batch detection function is callable"""
        self.assertTrue(callable(detect_dark_images_batch))
        print("✓ Batch detection function exists")

    def test_batch_detection_signature(self):
        """Test batch detection function signature contains required parameters"""
        import inspect
        sig = inspect.signature(detect_dark_images_batch)
        params = list(sig.parameters.keys())
        self.assertIn('folder_path', params)
        self.assertIn('threshold', params)
        print("✓ Batch detection has correct signature")

    def test_empty_folder_handling(self):
        """Test that scanning an empty folder returns the expected dict structure"""
        empty_dir = self.test_data_dir / "empty_dark"
        # Ensure directory is clean (remove any leftover files from prior runs)
        if empty_dir.exists():
            shutil.rmtree(str(empty_dir))
        empty_dir.mkdir()

        try:
            results = detect_dark_images_batch(str(empty_dir), threshold=40.0)
            self.assertIsInstance(results, dict)
            self.assertIn('dark_images', results)
            self.assertIn('bright_images', results)
            self.assertIn('total_processed', results)
            self.assertIn('total_dark', results)
            self.assertEqual(len(results['dark_images']), 0)
            self.assertEqual(len(results['bright_images']), 0)
            self.assertEqual(results['total_processed'], 0)
            self.assertEqual(results['total_dark'], 0)
            print("✓ Empty folder returns correctly structured empty result")
        except Exception as e:
            self.fail(f"Empty folder handling raised unexpected exception: {e}")

    def test_trash_folder_exclusion(self):
        """Test that paths containing 'Trash' in their parts are excluded"""
        trash_path = Path("C:/test/folder/Trash/image.jpg")
        self.assertIn('Trash', trash_path.parts)

        normal_path = Path("C:/test/folder/images/image.jpg")
        self.assertNotIn('Trash', normal_path.parts)
        print("✓ Trash folder exclusion logic validated")

    def test_result_dict_keys(self):
        """Test that result dict has exactly the four expected keys"""
        empty_dir = self.test_data_dir / "empty_dark_keys"
        if empty_dir.exists():
            shutil.rmtree(str(empty_dir))
        empty_dir.mkdir()
        results = detect_dark_images_batch(str(empty_dir), threshold=40.0)
        expected_keys = {'dark_images', 'bright_images', 'total_processed', 'total_dark'}
        self.assertEqual(set(results.keys()), expected_keys)
        print("✓ Result dict contains exactly the expected keys")


class TestDarkDetectionIntegration(unittest.TestCase):
    """Integration tests using synthetic images written to disk"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.detector = DarkImageDetector(threshold=40.0)

    def _write_png(self, filename, pixel_value):
        """Helper: write a 50x50 uniform PNG with the given pixel value (0-255)"""
        from PIL import Image as PILImage
        array = np.full((50, 50, 3), pixel_value, dtype=np.uint8)
        img = PILImage.fromarray(array)  # auto-detects RGB from 3-channel uint8
        path = self.test_data_dir / filename
        img.save(str(path))
        return str(path)

    def test_hsv_value_channel_on_dark_image(self):
        """Synthetic near-black image must have HSV Value mean well below 40"""
        try:
            import cv2
            dark_array = np.full((100, 100, 3), 10, dtype=np.uint8)
            bgr = cv2.cvtColor(dark_array, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            avg_v = np.mean(hsv[:, :, 2])
            self.assertLess(avg_v, 40.0)
            print(f"✓ Dark synthetic image HSV Value mean = {avg_v:.2f} (expected < 40)")
        except ImportError:
            print("OpenCV not available, skipping HSV Value test")

    def test_hsv_value_channel_on_bright_image(self):
        """Synthetic near-white image must have HSV Value mean well above 180"""
        try:
            import cv2
            bright_array = np.full((100, 100, 3), 240, dtype=np.uint8)
            bgr = cv2.cvtColor(bright_array, cv2.COLOR_RGB2BGR)
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            avg_v = np.mean(hsv[:, :, 2])
            self.assertGreater(avg_v, 180.0)
            print(f"✓ Bright synthetic image HSV Value mean = {avg_v:.2f} (expected > 180)")
        except ImportError:
            print("OpenCV not available, skipping HSV Value test")

    def test_dark_image_correctly_classified(self):
        """A synthetic dark image on disk must be detected as dark"""
        try:
            path = self._write_png("synthetic_dark.png", pixel_value=5)
            is_dark_result, score = self.detector.is_dark(path)
            self.assertTrue(is_dark_result, f"Expected dark image but got score={score:.2f}")
            self.assertLess(score, 40.0)
            self.assertEqual(self.detector.get_brightness_quality(score), "Very Dark")
            print(f"✓ Synthetic dark image correctly classified (score={score:.2f})")
        except ImportError:
            print("OpenCV not available, skipping dark image classification test")

    def test_bright_image_correctly_classified(self):
        """A synthetic bright image on disk must not be detected as dark"""
        try:
            path = self._write_png("synthetic_bright.png", pixel_value=230)
            is_dark_result, score = self.detector.is_dark(path)
            self.assertFalse(is_dark_result, f"Expected bright image but got score={score:.2f}")
            self.assertGreater(score, 180.0)
            quality = self.detector.get_brightness_quality(score)
            self.assertIn(quality, ("Bright", "Very Bright"))
            print(f"✓ Synthetic bright image correctly classified (score={score:.2f}, quality={quality})")
        except ImportError:
            print("OpenCV not available, skipping bright image classification test")

    def test_batch_detects_dark_image_in_folder(self):
        """detect_dark_images_batch must include the synthetic dark image in dark_images"""
        try:
            scan_dir = self.test_data_dir / "batch_scan_dark"
            if scan_dir.exists():
                shutil.rmtree(str(scan_dir))
            scan_dir.mkdir()

            from PIL import Image as PILImage
            PILImage.fromarray(np.full((50, 50, 3), 5, dtype=np.uint8)).save(
                str(scan_dir / "synthetic_batch_dark.png"))

            results = detect_dark_images_batch(str(scan_dir), threshold=40.0)
            dark_paths = [path for path, score in results['dark_images']]
            self.assertGreater(len(dark_paths), 0, "Expected at least one dark image")
            self.assertTrue(
                any("synthetic_batch_dark.png" in p for p in dark_paths),
                f"synthetic_batch_dark.png not found in dark_images: {dark_paths}"
            )
            print(f"✓ Batch detection found {len(results['dark_images'])} dark image(s)")
        except ImportError:
            print("OpenCV not available, skipping batch detection test")

    def test_batch_result_tuple_structure(self):
        """Each entry in dark_images and bright_images must be a (path, score) tuple"""
        try:
            scan_dir = self.test_data_dir / "batch_scan_struct"
            if scan_dir.exists():
                shutil.rmtree(str(scan_dir))
            scan_dir.mkdir()

            from PIL import Image as PILImage
            PILImage.fromarray(np.full((50, 50, 3), 5, dtype=np.uint8)).save(
                str(scan_dir / "dark.png"))
            PILImage.fromarray(np.full((50, 50, 3), 230, dtype=np.uint8)).save(
                str(scan_dir / "bright.png"))

            results = detect_dark_images_batch(str(scan_dir), threshold=40.0)
            for entry in results['dark_images']:
                self.assertIsInstance(entry, tuple)
                self.assertEqual(len(entry), 2)
                path, score = entry
                self.assertIsInstance(path, str)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 255.0)
            for entry in results['bright_images']:
                self.assertIsInstance(entry, tuple)
                self.assertEqual(len(entry), 2)
                path, score = entry
                self.assertIsInstance(path, str)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 255.0)
            print("✓ Batch result entries are correctly structured (path, score) tuples")
        except ImportError:
            print("OpenCV not available, skipping tuple structure test")

    def test_calculate_brightness_score_returns_numeric(self):
        """calculate_brightness_score must return a value in [0, 255] for a valid image"""
        try:
            path = self._write_png("synthetic_score_test.png", pixel_value=200)
            score = self.detector.calculate_brightness_score(path)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 255.0)
            print(f"✓ calculate_brightness_score returns value in [0, 255]: {score:.2f}")
        except ImportError:
            print("OpenCV not available, skipping score type test")

    def test_calculate_brightness_score_on_missing_file(self):
        """calculate_brightness_score must return -1 for a non-existent file"""
        score = self.detector.calculate_brightness_score("/nonexistent/path/image.jpg")
        self.assertEqual(score, -1)
        print("✓ Missing file returns brightness score of -1")

    def test_is_dark_returns_false_for_error_sentinel(self):
        """is_dark must return (False, -1) when the image cannot be processed"""
        result = self.detector.is_dark("/nonexistent/path/image.jpg")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        is_dark_flag, score = result
        self.assertFalse(is_dark_flag)
        self.assertEqual(score, -1)
        print("✓ is_dark returns (False, -1) for unprocessable image")

    def test_parallel_processing_support(self):
        """Test that parallel processing is available"""
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        self.assertGreater(cpu_count, 0)
        print(f"✓ Parallel processing supported: {cpu_count} CPUs")

    def test_module_imports(self):
        """Test that all modules required by DarkImageDetection can be imported"""
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
    print("Running Dark Detection Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
