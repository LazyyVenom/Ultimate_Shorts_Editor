#!/usr/bin/env python3
"""
Ultimate Shorts Editor - New Organized Entry Point
Demonstrates the improved component-based architecture
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import main

if __name__ == "__main__":
    sys.exit(main())
