"""
frequently used functions.
"""

import os
import json


def edit_json(obj, key, val):
    [item.__setitem__(key, val) for item in obj]

def dir_check(directory):
    if os.path.exists(directory):
        return None
    os.makedirs(directory)
