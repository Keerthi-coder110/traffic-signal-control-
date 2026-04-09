#!/usr/bin/env python3
"""
Hugging Face Space entry point.
This file is required for Spaces to recognize the application.
"""

import os
import sys

# Ensure HF_TOKEN is set
if not os.getenv("HF_TOKEN"):
    print("WARNING: HF_TOKEN not set. Using dummy token for demo.")
    os.environ["HF_TOKEN"] = "dummy_token_for_demo"

# Run inference
from inference import main

if __name__ == "__main__":
    print("Starting Traffic Signal Control Environment...")
    print("="*60)
    main()
