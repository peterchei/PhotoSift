# PhotoSift Test Suite

This directory contains regression tests for the PhotoSift application suite.

## Test Structure

### Test Files

- **`test_image_classification.py`** - Tests for AI-powered image classification (people vs screenshots)
- **`test_duplicate_detection.py`** - Tests for CLIP-based duplicate image detection
- **`test_blur_detection.py`** - Tests for Laplacian variance blur detection
- **`test_common_ui.py`** - Tests for shared UI components
- **`run_all_tests.py`** - Master test runner for all tests

### Test Data

The `test_data/` directory is automatically created for test fixtures. Add sample images here if needed for integration tests.

## Running Tests

### Run All Tests

```powershell
# From the tests directory
python run_all_tests.py

# Or using Python's unittest discovery
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Individual Test Modules

```powershell
# Image classification tests
python tests/test_image_classification.py

# Duplicate detection tests
python tests/test_duplicate_detection.py

# Blur detection tests
python tests/test_blur_detection.py

# Common UI tests
python tests/test_common_ui.py
```

### Run Specific Test Class

```powershell
python -m unittest tests.test_blur_detection.TestBlurDetection
```

### Run Specific Test Method

```powershell
python -m unittest tests.test_blur_detection.TestBlurDetection.test_detector_initialization
```

## Test Coverage

### Image Classification Tests
- ✅ Image extension validation
- ✅ Function existence and signatures
- ✅ Empty folder handling
- ✅ Result structure validation
- ✅ Model loading verification
- ✅ Confidence score validation

### Duplicate Detection Tests
- ✅ CLIP embedding generation
- ✅ Cosine similarity calculations
- ✅ Duplicate grouping logic
- ✅ Threshold validation
- ✅ Empty list handling
- ✅ Model loading verification

### Blur Detection Tests
- ✅ Detector initialization
- ✅ Custom threshold configuration
- ✅ Quality level categorization (Excellent/Good/Fair/Poor/Very Blurry)
- ✅ Laplacian variance calculations
- ✅ Batch processing functionality
- ✅ Trash folder exclusion logic
- ✅ Parallel processing support
- ✅ Empty folder handling

### Common UI Tests
- ✅ Color scheme completeness
- ✅ ModernButton factory methods
- ✅ TrashManager functionality
- ✅ ToolTip components
- ✅ StatusBar components
- ✅ Hex color validation

## Adding New Tests

When adding new features to PhotoSift, follow these guidelines:

### 1. Create Test File

Create a new test file following the naming convention `test_<feature>.py`:

```python
"""
Tests for <Feature Name>
Description of what this tests
"""

import unittest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from YourModule import your_function

class TestYourFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_something(self):
        """Test description"""
        self.assertTrue(True)
        print("✓ Test passed")

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### 2. Test Structure

Each test should:
- Have a descriptive name starting with `test_`
- Include a docstring explaining what it tests
- Use appropriate assertions
- Print success message for visibility
- Clean up any created resources

### 3. Test Types

**Unit Tests**: Test individual functions/methods in isolation
**Integration Tests**: Test components working together
**Regression Tests**: Ensure bugs don't reappear

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd tests
    python run_all_tests.py
```

## Test Requirements

Tests require the same dependencies as PhotoSift:
- Python 3.8+
- OpenCV (cv2)
- PIL/Pillow
- NumPy
- PyTorch
- Transformers (for CLIP)
- tkinter

Install development dependencies:
```powershell
pip install -r requirements.txt
```

## Expected Output

When all tests pass, you should see:

```
==================================================================================
                    PhotoSift Regression Test Suite
==================================================================================

test_blur_quality_levels (test_blur_detection.TestBlurDetection) ... ✓ Blur quality levels categorized correctly
ok
...
==================================================================================
Test Summary
==================================================================================
Tests run: 32
Successes: 32
Failures: 0
Errors: 0

✓ All tests passed! PhotoSift is working correctly.
```

## Troubleshooting

### Import Errors

If you see import errors, ensure:
1. You're running tests from the project root or tests directory
2. The `src` directory is in the Python path
3. All dependencies are installed

### Model Loading Errors

Some tests require AI models to be downloaded:
- CLIP models are downloaded automatically on first use
- Ensure internet connectivity for first run
- Models are cached in `~/.cache/huggingface/`

### Missing Test Data

The `test_data/` directory is created automatically. If you need specific test images:
1. Create sample images in `tests/test_data/`
2. Use small, synthetic images for fast tests
3. Document required test data in test docstrings

## Contributing

When contributing to PhotoSift:
1. Write tests for new features
2. Ensure all existing tests pass
3. Aim for high test coverage
4. Document test requirements
5. Update this README for significant changes

## License

These tests are part of the PhotoSift project and follow the same license.
