import os
import glob
from pathlib import Path

def clean_test_steps():
    """
    Cleans all files in the test_steps directory.
    This should be called before running any test suite.
    """
    test_steps_dir = Path("test_steps")
    
    # Create directory if it doesn't exist
    test_steps_dir.mkdir(exist_ok=True)
    
    # Remove all files in the directory
    files = glob.glob(str(test_steps_dir / "*.txt"))
    for file in files:
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Error removing {file}: {e}")
    
    print("Test steps directory cleaned successfully.") 