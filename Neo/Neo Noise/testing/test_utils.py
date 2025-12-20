"""
Neo Noise Test Utilities
Shared helper functions for logging and analysis.
"""

import os
import datetime
import numpy as np

LOG_FILE = "test_results.log"

def log(msg, passed=None):
    """
    Log message to console and file.
    If passed is True/False, validitate with [PASS]/[FAIL].
    """
    prefix = "[INFO]"
    if passed is True:
        prefix = "[PASS]"
    elif passed is False:
        prefix = "[FAIL]"
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"{prefix} {msg}"
    
    # Print to console
    print(formatted_msg)
    
    # Append to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {formatted_msg}\n")

def compare_fields(f1, f2, threshold=0.01):
    """Returns True if fields are identical within threshold."""
    if f1.shape != f2.shape:
        return False
    diff = np.mean(np.abs(f1 - f2))
    return diff < threshold
