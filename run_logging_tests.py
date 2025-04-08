#!/usr/bin/env python3
"""
Script to run the logging tests.
Usage: python run_logging_tests.py
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test module
from tests.test_logging import TestLogging

if __name__ == "__main__":
    # Create a test suite with the TestLogging class
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLogging)
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Exit with non-zero status if there were failures
    sys.exit(not result.wasSuccessful())
