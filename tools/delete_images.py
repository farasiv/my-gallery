# import json
# from pathlib import Path

# # ---------------- CONFIG ----------------
# FULL_DIR = Path("images/full")
# THUMBS_DIR = Path("images/thumbs")
# JSON_FILE = Path("images.json")
# # ----------------------------------------

# if not JSON_FILE.exists():
#     print("Error: images.json not found.")
#     exit()

# # Load current data
# with open(JSON_FILE, "r", encoding="utf-8") as f:
#     images_data = json.load(f)

# print(f"Current gallery has {len(images_data)} photos.")
# user_input = input("Which photo number(s) would you like to delete? (e.g., 5, 16, 9): ")

# # Parse input (handles spaces and commas)
# targets = [id.strip().zfill(3) for id in user_input.replace(",", " ").split()]

# deleted_count = 0
# new_images_data = []

# for item in images_data:
#     # Extract number from filename (e.g., '005' from 'photo_005.jpg')
#     filename = item["file"]
#     file_num = filename.split("_")[1].split(".")[0]

#     if file_num in targets:
#         # Delete physical files
#         full_path = FULL_DIR / filename
#         thumb_path = THUMBS_DIR / filename
        
#         if full_path.exists(): full_path.unlink()
#         if thumb_path.exists(): thumb_path.unlink()
        
#         print(f"Deleted: {filename}")
#         deleted_count += 1
#     else:
#         # Keep items that weren't targeted
#         new_images_data.append(item)

# # Save updated JSON
# with open(JSON_FILE, "w", encoding="utf-8") as f:
#     json.dump(new_images_data, f, indent=2)

# print(f"\nDeletion completed. {deleted_count} files removed.")
# print("Run 'py prepare_images.py' to fill the gaps with new photos.")

import json
from pathlib import Path

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).parent.parent
IMAGE_ROOT = BASE_DIR / "images"
DATA_DIR = BASE_DIR / "data"
# ----------------------------------------

album_name = input("Which album are you editing? ").strip().lower().replace(" ", "_")
ALBUM_JSON = DATA_DIR / f"{album_name}.json"
ALBUM_FULL = IMAGE_ROOT / album_name / "full"
ALBUM_THUMBS = IMAGE_ROOT / album_name / "thumbs"

if not ALBUM_JSON.exists():
    print(f"Error: Album '{album_name}' not found.")
    exit()

with open(ALBUM_JSON, "r", encoding="utf-8") as f:
    images_data = json.load(f)

user_input = input("Which photo number(s) to delete? (e.g., 5, 9): ")
targets = [id.strip().zfill(3) for id in user_input.replace(",", " ").split()]

new_data = []
for item in images_data:
    file_num = item["file"].split("_")[1].split(".")[0]
    if file_num in targets:
        (ALBUM_FULL / item["file"]).unlink(missing_ok=True)
        (ALBUM_THUMBS / item["file"]).unlink(missing_ok=True)
        print(f"Deleted {item['file']}")
    else:
        new_data.append(item)

with open(ALBUM_JSON, "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=2)

print("Done.")