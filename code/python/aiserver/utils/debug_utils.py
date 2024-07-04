# utils/debug_utils.py

import sys

def debug_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)