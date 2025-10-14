"""
PhotoSift Test Runner
Runs all regression tests for PhotoSift application suite
"""

import unittest
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_all_tests():
    """Run all PhotoSift regression tests"""
    
    print("=" * 80)
    print(" " * 20 + "PhotoSift Regression Test Suite")
    print("=" * 80)
    print()
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print()
        print("✓ All tests passed! PhotoSift is working correctly.")
        return 0
    else:
        print()
        print("✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
