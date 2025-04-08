#!/usr/bin/env python3
"""
Script to run all tests for the Metropole.AI project.
Usage: python run_tests.py
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Exit with non-zero status if there were failures
    sys.exit(not result.wasSuccessful())
