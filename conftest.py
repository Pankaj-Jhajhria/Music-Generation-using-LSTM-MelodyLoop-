import os
import sys

# Ensure root directory is in sys.path when pytest is invoked directly
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
