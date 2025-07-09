import os
import time


def clean_screenshots_dir(screenshots_dir="screenshots", age_minutes=0):
    """Deletes all .png and .zip files in the screenshots directory.
    If age_minutes > 0, only deletes files older than that age."""
    path = os.path.abspath(screenshots_dir)
    os.makedirs(path, exist_ok=True)
    now = time.time()
    cutoff = now - (age_minutes * 60)

    for file in os.listdir(path):
        if file.endswith((".png", ".zip")):
            full_path = os.path.join(path, file)
            try:
                if age_minutes == 0 or os.path.getmtime(full_path) < cutoff:
                    os.remove(full_path)
                    print(f"🗑️ Removed old file: {file}")
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")
