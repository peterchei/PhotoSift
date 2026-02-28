"""
Tests for Safe Content Detection functionality.
All tests are unit tests that do NOT load the CLIP model.
"""

import unittest
import os
import sys
import inspect
import shutil
from pathlib import Path

# Ensure Unicode output works on Windows cp1252 terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from SafeContentDetection import (
    LABELS, SafeContentDetector, scan_folder_safe_content, scan_content_batch
)

REQUIRED_CATEGORIES = {'safe', 'adult', 'violent', 'disturbing'}


class TestSafeContentDetection(unittest.TestCase):
    """Unit tests for Safe Content Detection — no CLIP model load required."""

    def setUp(self):
        self.test_data_dir = Path(__file__).parent / "test_data" / "safe_content"
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)
        self.test_data_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

    # --- LABELS dict ---

    def test_labels_dict_exists(self):
        """LABELS dict exists and has exactly 4 keys."""
        self.assertIsNotNone(LABELS)
        self.assertIsInstance(LABELS, dict)
        self.assertEqual(len(LABELS), 4)
        print("✓ LABELS dict exists with 4 keys")

    def test_labels_have_required_categories(self):
        """LABELS keys are exactly {safe, adult, violent, disturbing}."""
        self.assertEqual(set(LABELS.keys()), REQUIRED_CATEGORIES)
        print("✓ LABELS has required categories: safe, adult, violent, disturbing")

    def test_each_category_has_prompts(self):
        """Each category has at least 5 text prompts."""
        for category, prompts in LABELS.items():
            self.assertGreaterEqual(
                len(prompts), 5,
                f"Category '{category}' has only {len(prompts)} prompts (need ≥ 5)")
        print("✓ Each category has ≥ 5 text prompts")

    def test_safe_prompts_are_strings(self):
        """All prompts are non-empty strings."""
        for category, prompts in LABELS.items():
            for prompt in prompts:
                self.assertIsInstance(prompt, str,
                    f"Prompt in '{category}' is not a string: {prompt!r}")
                self.assertGreater(len(prompt.strip()), 0,
                    f"Empty prompt found in '{category}'")
        print("✓ All prompts are non-empty strings")

    # --- SafeContentDetector class ---

    def test_detector_class_exists(self):
        """SafeContentDetector is importable and instantiable."""
        detector = SafeContentDetector()
        self.assertIsNotNone(detector)
        print("✓ SafeContentDetector is importable and instantiable")

    def test_classify_image_method_exists(self):
        """SafeContentDetector has a callable classify_image method."""
        detector = SafeContentDetector()
        self.assertTrue(callable(getattr(detector, 'classify_image', None)))
        print("✓ SafeContentDetector.classify_image is callable")

    def test_get_content_rating_method_exists(self):
        """SafeContentDetector has a callable get_content_rating method."""
        detector = SafeContentDetector()
        self.assertTrue(callable(getattr(detector, 'get_content_rating', None)))
        print("✓ SafeContentDetector.get_content_rating is callable")

    # --- scan_folder_safe_content function ---

    def test_scan_folder_function_exists(self):
        """scan_folder_safe_content is callable."""
        self.assertTrue(callable(scan_folder_safe_content))
        print("✓ scan_folder_safe_content is callable")

    def test_scan_folder_signature(self):
        """scan_folder_safe_content has a folder_path parameter."""
        sig = inspect.signature(scan_folder_safe_content)
        self.assertIn('folder_path', sig.parameters)
        print("✓ scan_folder_safe_content has folder_path parameter")

    def test_result_dict_keys(self):
        """Scanning an empty folder returns a dict with all 7 expected keys."""
        result = scan_folder_safe_content(str(self.test_data_dir))
        expected_keys = {
            'safe_images', 'adult_images', 'violent_images', 'disturbing_images',
            'error_images', 'total_processed', 'total_flagged'
        }
        self.assertEqual(set(result.keys()), expected_keys)
        print("✓ Result dict has all 7 expected keys")

    # --- get_content_rating ---

    def test_content_rating_safe(self):
        """High-confidence safe image → 'Safe'."""
        detector = SafeContentDetector()
        rating = detector.get_content_rating('safe', 0.9)
        self.assertEqual(rating, 'Safe')
        print("✓ get_content_rating('safe', 0.9) → 'Safe'")

    def test_content_rating_adult(self):
        """High-confidence adult image → 'Adult Content'."""
        detector = SafeContentDetector()
        rating = detector.get_content_rating('adult', 0.8)
        self.assertEqual(rating, 'Adult Content')
        print("✓ get_content_rating('adult', 0.8) → 'Adult Content'")

    def test_content_rating_violent(self):
        """High-confidence violent image → 'Violent / Gore'."""
        detector = SafeContentDetector()
        rating = detector.get_content_rating('violent', 0.7)
        self.assertEqual(rating, 'Violent / Gore')
        print("✓ get_content_rating('violent', 0.7) → 'Violent / Gore'")

    def test_content_rating_disturbing(self):
        """High-confidence disturbing image → 'Disturbing'."""
        detector = SafeContentDetector()
        rating = detector.get_content_rating('disturbing', 0.6)
        self.assertEqual(rating, 'Disturbing')
        print("✓ get_content_rating('disturbing', 0.6) → 'Disturbing'")

    def test_content_rating_low_confidence_safe(self):
        """Low-confidence safe image → 'Likely Safe'."""
        detector = SafeContentDetector()
        rating = detector.get_content_rating('safe', 0.51)
        self.assertEqual(rating, 'Likely Safe')
        print("✓ get_content_rating('safe', 0.51) → 'Likely Safe'")

    # --- Softmax bounds ---

    def test_softmax_confidence_bounds(self):
        """Softmax over 4 category values sums to 1.0, each value in [0, 1]."""
        import numpy as np

        # Simulate per-category summed probabilities from CLIP
        raw = np.array([0.5, 0.2, 0.15, 0.15])
        exp = np.exp(raw - np.max(raw))
        softmax = exp / exp.sum()

        for val in softmax:
            self.assertGreaterEqual(float(val), 0.0)
            self.assertLessEqual(float(val), 1.0)
        self.assertAlmostEqual(float(softmax.sum()), 1.0, places=5)
        print("✓ Softmax over 4 categories sums to 1.0 with values in [0, 1]")

    # --- Empty folder ---

    def test_empty_folder_handling(self):
        """Scanning an empty folder returns zeroed result dict with correct structure."""
        result = scan_folder_safe_content(str(self.test_data_dir))
        self.assertEqual(result['total_processed'], 0)
        self.assertEqual(result['total_flagged'], 0)
        self.assertEqual(result['safe_images'], [])
        self.assertEqual(result['adult_images'], [])
        self.assertEqual(result['violent_images'], [])
        self.assertEqual(result['disturbing_images'], [])
        self.assertEqual(result['error_images'], [])
        print("✓ Empty folder scan returns zeroed result dict")

    # --- Trash exclusion ---

    def test_trash_folder_exclusion(self):
        """Images inside a Trash subfolder are excluded from scan paths."""
        trash_dir = self.test_data_dir / "Trash"
        trash_dir.mkdir(parents=True, exist_ok=True)

        # Create a dummy image in Trash
        from PIL import Image as PILImage
        dummy = PILImage.new("RGB", (100, 100), color=(128, 128, 128))
        dummy.save(str(trash_dir / "trash_image.jpg"))

        # Scanning should skip Trash contents — returns zero processed (no CLIP call needed)
        result = scan_folder_safe_content(str(self.test_data_dir))
        self.assertEqual(result['total_processed'], 0,
                         "Images in Trash directory should be excluded from scan")
        print("✓ Images in Trash subdirectory are excluded from scan")


if __name__ == '__main__':
    print("=" * 70)
    print("Running Safe Content Detection Tests")
    print("=" * 70)
    unittest.main(verbosity=2)
