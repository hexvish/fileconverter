
import sys
import os

# Ensure the current directory is in sys.path so 'src' can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.main import main

if __name__ == "__main__":
    main()
