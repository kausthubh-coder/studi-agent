#!/usr/bin/env python3
"""
Run script for Canvas Terminal Agent
"""

import os
import sys
import asyncio

# Add the parent directory to the path so Python can treat 'agent' as a package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Using a direct import of the module in the same directory
import main

if __name__ == "__main__":
    try:
        main.main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0) 