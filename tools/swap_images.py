# import json
# from pathlib import Path

# # ---------------- CONFIG ----------------
# FULL_DIR = Path("images/full")
# THUMBS_DIR = Path("images/thumbs")
# JSON_FILE = Path("images.json")
# # ----------------------------------------

# def rename_file(old_name, new_name):
#     # Renames both full and thumb versions
#     p_full_old, p_full_new = FULL_DIR / old_name, FULL_DIR / new_name
#     p_thumb_old, p_thumb_new = THUMBS_DIR / old_name, THUMBS_DIR / new_name
    
#     if p_full_old.exists(): p_full_old.rename(p_full_new)
#     if p_thumb_old.exists(): p_thumb_old.rename(p_thumb_new)

# if not JSON_FILE.exists():
#     print("Error: images.json not found.")
#     exit()

# with open(JSON_FILE, "r", encoding="utf-8") as f:
#     images_data = json.load(f)

# print(f"Gallery has {len(images_data)} photos.")
# val1 = input("Enter first photo number to swap (e.g. 2): ").strip().zfill(3)
# val2 = input("Enter second photo number to swap (e.g. 4): ").strip().zfill(3)

# # Find the items in the list
# idx1, item1 = next(((i, x) for i, x in enumerate(images_data) if x['file'].split('_')[1].startswith(val1)), (None, None))
# idx2, item2 = next(((i, x) for i, x in enumerate(images_data) if x['file'].split('_')[1].startswith(val2)), (None, None))

# if item1 is None or item2 is None:
#     print("Error: One or both photo numbers not found.")
#     exit()

# # 1. Physical Swap (Renaming files)
# # We use a temporary name to avoid overwriting if the extension is the same
# file1, file2 = item1['file'], item2['file']
# ext1, ext2 = Path(file1).suffix, Path(file2).suffix

# temp_name = f"temp_swap{ext1}"
# rename_file(file1, temp_name)
# rename_file(file2, f"photo_{val1}{ext2}")
# rename_file(temp_name, f"photo_{val2}{ext1}")

# # 2. JSON Swap (Update the filenames and swap positions)
# item1['file'] = f"photo_{val2}{ext1}"
# item2['file'] = f"photo_{val1}{ext2}"

# images_data[idx1], images_data[idx2] = item2, item1

# # 3. Sort to maintain order
# images_data.sort(key=lambda x: x["file"])

# with open(JSON_FILE, "w", encoding="utf-8") as f:
#     json.dump(images_data, f, indent=2)

# print(f"Done! Swapped photo {val1} and {val2} successfully.")

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

val1 = input("First photo number: ").strip().zfill(3)
val2 = input("Second photo number: ").strip().zfill(3)

def get_item(num):
    return next(((i, x) for i, x in enumerate(images_data) if x['file'].split('_')[1].startswith(num)), (None, None))

idx1, item1 = get_item(val1)
idx2, item2 = get_item(val2)

if item1 and item2:
    # Rename physical files
    f1, f2 = item1['file'], item2['file']
    ext1, ext2 = Path(f1).suffix, Path(f2).suffix
    
    # Temp rename to avoid collision
    (ALBUM_FULL / f1).rename(ALBUM_FULL / f"temp{ext1}")
    (ALBUM_THUMBS / f1).rename(ALBUM_THUMBS / f"temp{ext1}")
    
    (ALBUM_FULL / f2).rename(ALBUM_FULL / f"photo_{val1}{ext2}")
    (ALBUM_THUMBS / f2).rename(ALBUM_THUMBS / f"photo_{val1}{ext2}")
    
    (ALBUM_FULL / f"temp{ext1}").rename(ALBUM_FULL / f"photo_{val2}{ext1}")
    (ALBUM_THUMBS / f"temp{ext1}").rename(ALBUM_THUMBS / f"photo_{val2}{ext1}")

    # Update JSON
    item1['file'] = f"photo_{val2}{ext1}"
    item2['file'] = f"photo_{val1}{ext2}"
    images_data[idx1], images_data[idx2] = item2, item1
    images_data.sort(key=lambda x: x["file"])

    with open(ALBUM_JSON, "w", encoding="utf-8") as f:
        json.dump(images_data, f, indent=2)
    print("Swap successful.")
else:
    print("One or both numbers not found.")