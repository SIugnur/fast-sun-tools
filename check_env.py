import sys
import os

print("========================================")
print("FastSunTools - Environment Check")
print("========================================")
print()

# Check Python
try:
    import PyQt5
    print("✓ PyQt5 installed")
except ImportError:
    print("✗ PyQt5 not installed")
    sys.exit(1)

try:
    from PIL import Image
    print("✓ Pillow installed")
except ImportError:
    print("✗ Pillow not installed")
    sys.exit(1)

try:
    import easyocr
    print("✓ EasyOCR installed")
except ImportError:
    print("✗ EasyOCR not installed")
    sys.exit(1)

try:
    import mss
    print("✓ mss installed")
except ImportError:
    print("✗ mss not installed")
    sys.exit(1)

try:
    import pyperclip
    print("✓ pyperclip installed")
except ImportError:
    print("✗ pyperclip not installed")
    sys.exit(1)

print()
print("✓ All dependencies are installed!")
print()
print("Starting FastSunTools...")
print("========================================")

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
