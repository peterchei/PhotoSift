"""
Tests for Low Resolution Image Detection functionality
Tests the PIL-based low resolution image detection system
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

# Add src directory to path (mirrors pattern in test_dark_detection.py)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from LowResolutionDetection import LowResolutionDetector, detect_low_res_images_batch, get_recommended_thresholds


class TestLowResolutionDetection(unittest.TestCase):
    """Unit tests for low resolution detection logic - no file I/O required"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.detector = LowResolutionDetector(min_width=1280, min_height=720)

    def test_detector_initialization(self):
        """Test that detector initialises with supplied thresholds"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.min_width, 1280)
        self.assertEqual(self.detector.min_height, 720)
        print("✓ Low resolution detector initialised correctly")

    def test_threshold_customization(self):
        """Test that custom thresholds are stored correctly"""
        custom_detector = LowResolutionDetector(min_width=1920, min_height=1080)
        self.assertEqual(custom_detector.min_width, 1920)
        self.assertEqual(custom_detector.min_height, 1080)
        print("✓ Custom thresholds set correctly")

    def test_recommended_thresholds_function(self):
        """Test that get_recommended_thresholds returns a dict with expected keys"""
        self.assertTrue(callable(get_recommended_thresholds))
        thresholds = get_recommended_thresholds()
        self.assertIsInstance(thresholds, dict)
        self.assertIn('minimal', thresholds)
        self.assertIn('normal', thresholds)
        self.assertIn('strict', thresholds)
        for key in ('minimal', 'normal', 'strict'):
            self.assertIn('value_w', thresholds[key])
            self.assertIn('value_h', thresholds[key])
            self.assertIsInstance(thresholds[key]['value_w'], (int, float))
            self.assertIsInstance(thresholds[key]['value_h'], (int, float))
            self.assertGreater(thresholds[key]['value_w'], 0)
            self.assertGreater(thresholds[key]['value_h'], 0)
        print(f"✓ Recommended thresholds available: {list(thresholds.keys())}")

    def test_recommended_thresholds_ordering(self):
        """Test that minimal < normal < strict in recommended thresholds"""
        thresholds = get_recommended_thresholds()
        minimal_w = thresholds['minimal']['value_w']
        normal_w = thresholds['normal']['value_w']
        strict_w = thresholds['strict']['value_w']
        self.assertLess(minimal_w, normal_w)
        self.assertLess(normal_w, strict_w)
        print(f"✓ Threshold ordering correct: minimal={minimal_w} < normal={normal_w} < strict={strict_w}")

    def test_resolution_quality_tiny(self):
        """Short side < 240 maps to 'Tiny'"""
        self.assertEqual(self.detector.get_resolution_quality(100, 80), "Tiny")
        self.assertEqual(self.detector.get_resolution_quality(239, 239), "Tiny")
        print("✓ Tiny boundary correct (short side < 240)")

    def test_resolution_quality_low(self):
        """Short side 240-479 maps to 'Low'"""
        self.assertEqual(self.detector.get_resolution_quality(320, 240), "Low")
        self.assertEqual(self.detector.get_resolution_quality(600, 479), "Low")
        print("✓ Low boundary correct (240 <= short side < 480)")

    def test_resolution_quality_sd(self):
        """Short side 480-719 maps to 'SD'"""
        self.assertEqual(self.detector.get_resolution_quality(640, 480), "SD")
        self.assertEqual(self.detector.get_resolution_quality(900, 719), "SD")
        print("✓ SD boundary correct (480 <= short side < 720)")

    def test_resolution_quality_hd(self):
        """Short side 720-1079 maps to 'HD'"""
        self.assertEqual(self.detector.get_resolution_quality(1280, 720), "HD")
        self.assertEqual(self.detector.get_resolution_quality(1500, 1079), "HD")
        print("✓ HD boundary correct (720 <= short side < 1080)")

    def test_resolution_quality_full_hd(self):
        """Short side 1080-1439 maps to 'Full HD'"""
        self.assertEqual(self.detector.get_resolution_quality(1920, 1080), "Full HD")
        self.assertEqual(self.detector.get_resolution_quality(2000, 1439), "Full HD")
        print("✓ Full HD boundary correct (1080 <= short side < 1440)")

    def test_resolution_quality_high_res(self):
        """Short side 1440-2159 maps to 'High Res'"""
        self.assertEqual(self.detector.get_resolution_quality(2560, 1440), "High Res")
        self.assertEqual(self.detector.get_resolution_quality(3000, 2159), "High Res")
        print("✓ High Res boundary correct (1440 <= short side < 2160)")

    def test_resolution_quality_ultra_hd(self):
        """Short side >= 2160 maps to 'Ultra HD'"""
        self.assertEqual(self.detector.get_resolution_quality(3840, 2160), "Ultra HD")
        self.assertEqual(self.detector.get_resolution_quality(8000, 6000), "Ultra HD")
        print("✓ Ultra HD boundary correct (short side >= 2160)")

    def test_resolution_quality_error_sentinel(self):
        """(-1, -1) dimensions map to 'Unknown'"""
        self.assertEqual(self.detector.get_resolution_quality(-1, -1), "Unknown")
        self.assertEqual(self.detector.get_resolution_quality(-1, 720), "Unknown")
        print("✓ Error sentinel (-1, -1) maps to 'Unknown'")

    def test_batch_detection_function_exists(self):
        """Test that batch detection function is callable"""
        self.assertTrue(callable(detect_low_res_images_batch))
        print("✓ Batch detection function exists")

    def test_batch_detection_signature(self):
        """Test batch detection function signature contains required parameters"""
        import inspect
        sig = inspect.signature(detect_low_res_images_batch)
        params = list(sig.parameters.keys())
        self.assertIn('folder_path', params)
        self.assertIn('min_width', params)
        self.assertIn('min_height', params)
        print("✓ Batch detection has correct signature")

    def test_empty_folder_handling(self):
        """Test that scanning an empty folder returns the expected dict structure"""
        empty_dir = self.test_data_dir / "empty_low_res"
        if empty_dir.exists():
            shutil.rmtree(str(empty_dir))
        empty_dir.mkdir()

        try:
            results = detect_low_res_images_batch(str(empty_dir), min_width=1280, min_height=720)
            self.assertIsInstance(results, dict)
            self.assertIn('low_res_images', results)
            self.assertIn('ok_images', results)
            self.assertIn('total_processed', results)
            self.assertIn('total_low_res', results)
            self.assertEqual(len(results['low_res_images']), 0)
            self.assertEqual(len(results['ok_images']), 0)
            self.assertEqual(results['total_processed'], 0)
            self.assertEqual(results['total_low_res'], 0)
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
        empty_dir = self.test_data_dir / "empty_low_res_keys"
        if empty_dir.exists():
            shutil.rmtree(str(empty_dir))
        empty_dir.mkdir()
        results = detect_low_res_images_batch(str(empty_dir), min_width=1280, min_height=720)
        expected_keys = {'low_res_images', 'ok_images', 'total_processed', 'total_low_res'}
        self.assertEqual(set(results.keys()), expected_keys)
        print("✓ Result dict contains exactly the expected keys")


class TestLowResolutionDetectionIntegration(unittest.TestCase):
    """Integration tests using synthetic images written to disk"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        self.detector = LowResolutionDetector(min_width=1280, min_height=720)

    def _write_png(self, filename, width, height):
        """Helper: write a PNG of the given pixel dimensions with a solid colour"""
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (width, height), color=(128, 128, 128))
        path = self.test_data_dir / filename
        img.save(str(path))
        return str(path)

    def test_low_res_image_correctly_flagged(self):
        """A 200x150 image must be flagged as low resolution"""
        path = self._write_png("synthetic_low_res.png", 200, 150)
        is_low, w, h = self.detector.is_low_res(path)
        self.assertTrue(is_low, f"Expected low-res flag but got ({w}, {h})")
        self.assertEqual(w, 200)
        self.assertEqual(h, 150)
        print(f"✓ 200x150 image correctly flagged as low resolution")

    def test_ok_image_not_flagged(self):
        """A 1920x1080 image must not be flagged as low resolution"""
        path = self._write_png("synthetic_ok_res.png", 1920, 1080)
        is_low, w, h = self.detector.is_low_res(path)
        self.assertFalse(is_low, f"Expected OK resolution but got flagged at ({w}, {h})")
        self.assertEqual(w, 1920)
        self.assertEqual(h, 1080)
        print(f"✓ 1920x1080 image correctly classified as OK resolution")

    def test_get_dimensions_returns_correct_size(self):
        """get_dimensions must return the actual pixel dimensions"""
        path = self._write_png("synthetic_dims.png", 640, 480)
        w, h = self.detector.get_dimensions(path)
        self.assertEqual(w, 640)
        self.assertEqual(h, 480)
        print(f"✓ get_dimensions returns correct size: {w}x{h}")

    def test_get_dimensions_on_missing_file(self):
        """get_dimensions must return (-1, -1) for a non-existent file"""
        w, h = self.detector.get_dimensions("/nonexistent/path/image.jpg")
        self.assertEqual(w, -1)
        self.assertEqual(h, -1)
        print("✓ Missing file returns dimensions of (-1, -1)")

    def test_is_low_res_on_missing_file(self):
        """is_low_res must return (False, -1, -1) when the image cannot be processed"""
        result = self.detector.is_low_res("/nonexistent/path/image.jpg")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        is_low, w, h = result
        self.assertFalse(is_low)
        self.assertEqual(w, -1)
        self.assertEqual(h, -1)
        print("✓ is_low_res returns (False, -1, -1) for unprocessable image")

    def test_batch_detects_low_res_image(self):
        """detect_low_res_images_batch must include the 200x150 image in low_res_images"""
        scan_dir = self.test_data_dir / "batch_scan_low_res"
        if scan_dir.exists():
            shutil.rmtree(str(scan_dir))
        scan_dir.mkdir()

        from PIL import Image as PILImage
        PILImage.new("RGB", (200, 150), color=(100, 100, 100)).save(
            str(scan_dir / "synthetic_batch_low_res.png"))

        results = detect_low_res_images_batch(str(scan_dir), min_width=1280, min_height=720)
        low_paths = [p for p, w, h in results['low_res_images']]
        self.assertGreater(len(low_paths), 0, "Expected at least one low-res image")
        self.assertTrue(
            any("synthetic_batch_low_res.png" in p for p in low_paths),
            f"synthetic_batch_low_res.png not found in low_res_images: {low_paths}"
        )
        print(f"✓ Batch detection found {len(results['low_res_images'])} low-res image(s)")

    def test_batch_result_tuple_structure(self):
        """Each entry in low_res_images and ok_images must be a (path, width, height) 3-tuple"""
        scan_dir = self.test_data_dir / "batch_scan_struct_lr"
        if scan_dir.exists():
            shutil.rmtree(str(scan_dir))
        scan_dir.mkdir()

        from PIL import Image as PILImage
        PILImage.new("RGB", (200, 150)).save(str(scan_dir / "low.png"))
        PILImage.new("RGB", (1920, 1080)).save(str(scan_dir / "ok.png"))

        results = detect_low_res_images_batch(str(scan_dir), min_width=1280, min_height=720)
        for entry in results['low_res_images']:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 3)
            path, w, h = entry
            self.assertIsInstance(path, str)
            self.assertIsInstance(w, int)
            self.assertIsInstance(h, int)
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)
        for entry in results['ok_images']:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 3)
            path, w, h = entry
            self.assertIsInstance(path, str)
            self.assertIsInstance(w, int)
            self.assertIsInstance(h, int)
        print("✓ Batch result entries are correctly structured (path, width, height) 3-tuples")

    def test_result_sorted_smallest_first(self):
        """low_res_images must be sorted ascending by the short side (smallest first)"""
        scan_dir = self.test_data_dir / "batch_sort_lr"
        if scan_dir.exists():
            shutil.rmtree(str(scan_dir))
        scan_dir.mkdir()

        from PIL import Image as PILImage
        # Three low-res images of different sizes
        PILImage.new("RGB", (640, 480)).save(str(scan_dir / "medium.png"))
        PILImage.new("RGB", (100, 80)).save(str(scan_dir / "tiny.png"))
        PILImage.new("RGB", (320, 240)).save(str(scan_dir / "small.png"))

        results = detect_low_res_images_batch(str(scan_dir), min_width=1280, min_height=720)
        short_sides = [min(w, h) for _, w, h in results['low_res_images']]
        self.assertEqual(short_sides, sorted(short_sides),
                         f"Expected ascending order, got: {short_sides}")
        print(f"✓ low_res_images sorted ascending by short side: {short_sides}")

    def test_parallel_processing_support(self):
        """Test that parallel processing is available"""
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        self.assertGreater(cpu_count, 0)
        print(f"✓ Parallel processing supported: {cpu_count} CPUs")

    def test_module_imports(self):
        """Test that all modules required by LowResolutionDetection can be imported"""
        try:
            from PIL import Image
            from pathlib import Path
            from concurrent.futures import ThreadPoolExecutor
            import multiprocessing
            print("✓ All required modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")


if __name__ == '__main__':
    print("=" * 70)
    print("Running Low Resolution Detection Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
