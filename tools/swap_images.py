# NOT WORKING

import json
import os
from pathlib import Path

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).parent.parent
IMAGE_ROOT = BASE_DIR / "images"
DATA_DIR = BASE_DIR / "data"
# ----------------------------------------

def select_from_options(options, prompt):
    print(f"\nAvailable {prompt}s:")
    for i, opt in enumerate(options, 1):
        print(f"[{i}] {opt}")
    choice = int(input(f"Select {prompt} (number): ")) - 1
    return options[choice]

def reindex_album(year, album_slug, images_data, ALBUM_THUMBS, ALBUM_JSON):
    """Normalizes all filenames using a two-pass approach to prevent WinError 183."""
    print("\n🔄 Re-indexing all images (Two-Pass Normalization)...")
    
    # Pass 1: Move everything to a temporary unique name
    temp_names = []
    for idx, item in enumerate(images_data, 1):
        old_file = item['file']
        temp_name = f"tmp_reindex_{idx}_{old_file}"
        (ALBUM_THUMBS / old_file).rename(ALBUM_THUMBS / temp_name)
        temp_names.append((temp_name, Path(old_file).suffix))

    # Pass 2: Move from temporary names to final sequential names
    new_data = []
    for idx, (temp_name, suffix) in enumerate(temp_names, 1):
        new_name = f"photo_{idx:03d}{suffix}"
        (ALBUM_THUMBS / temp_name).rename(ALBUM_THUMBS / new_name)
        
        # Update the JSON entry
        images_data[idx-1]['file'] = new_name
        new_data.append(images_data[idx-1])
        print(f"  Item {idx}: -> {new_name}")

    # Save the final JSON
    with open(ALBUM_JSON, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)
    
    return new_data

def run_swap():
    # 1. Select Year
    years = sorted([d.name for d in IMAGE_ROOT.iterdir() if d.is_dir() and d.name.isdigit()], reverse=True)
    if not years: return
    year = select_from_options(years, "Year")

    # 2. Select Album
    album_options = sorted([d.name for d in (IMAGE_ROOT / year).iterdir() if d.is_dir()])
    if not album_options: return
    album_slug = select_from_options(album_options, "Album")

    # 3. Setup Paths
    ALBUM_JSON = DATA_DIR / year / f"{album_slug}.json"
    ALBUM_DIR = IMAGE_ROOT / year / album_slug
    ALBUM_THUMBS = ALBUM_DIR / "thumbs"

    with open(ALBUM_JSON, "r", encoding="utf-8") as f:
        images_data = json.load(f)

    # Show current list to user
    print(f"\nCurrently {len(images_data)} images in {album_slug}")
    
    val1 = input("\nFirst photo number to swap (e.g. 1): ").strip().zfill(3)
    val2 = input("Second photo number to swap (e.g. 5): ").strip().zfill(3)

    # Match by partial string to be flexible with extensions
    def get_item(num):
        return next(((i, x) for i, x in enumerate(images_data) if f"_{num}." in x['file']), (None, None))

    idx1, item1 = get_item(val1)
    idx2, item2 = get_item(val2)

    if item1 and item2:
        # Perform the list swap
        images_data[idx1], images_data[idx2] = images_data[idx2], images_data[idx1]
        
        # Immediately re-index everything to fix names and thumbnails
        reindex_album(year, album_slug, images_data, ALBUM_THUMBS, ALBUM_JSON)
        
        print(f"\n✅ Swap and Re-index successful.")
    else:
        print("❌ One or both numbers not found.")

if __name__ == "__main__":
    run_swap()