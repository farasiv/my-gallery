import json
import requests
import shutil
import base64
import os
from pathlib import Path
from PIL import Image, ImageOps

# ---------------- CONFIG ----------------
API_KEY = "94761cb08cb48333e177d234749f7521"
BASE_DIR = Path(__file__).parent.parent
INCOMING_DIR = BASE_DIR / "incoming"
DATA_DIR = BASE_DIR / "data"
IMAGE_ROOT = BASE_DIR / "images"
MENU_FILE = BASE_DIR / "menu.html"

THUMB_MAX_SIZE = (600, 600)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Ensure base directories exist
DATA_DIR.mkdir(exist_ok=True)
IMAGE_ROOT.mkdir(exist_ok=True)
INCOMING_DIR.mkdir(exist_ok=True)
# ----------------------------------------

def upload_to_imgbb(image_path):
    """Uploads an image to ImgBB and returns the direct display URL"""
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(image_path, "rb") as file:
            base64_image = base64.b64encode(file.read())
            payload = {
                "key": API_KEY,
                "image": base64_image,
            }
            res = requests.post(url, data=payload)
            if res.status_code == 200:
                return res.json()['data']['url']
            else:
                print(f"❌ ImgBB Upload Error: {res.text}")
                return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def rebuild_master_files():
    """Groups albums by year for a nested website menu"""
    print("\nRefreshing master files...")
    
    structure = {} # Dictionary to hold { "2025": [album1, album2], "2026": [...] }
    
    for year_folder in sorted(IMAGE_ROOT.iterdir()):
        if year_folder.is_dir() and year_folder.name.isdigit():
            year = year_folder.name
            structure[year] = []
            
            for album_folder in sorted(year_folder.iterdir()):
                if album_folder.is_dir() and (album_folder / "thumbs").exists():
                    album_slug = album_folder.name
                    # Keep the name exactly as the folder is named, just replace underscores
                    display_name = album_slug.replace('_', ' ').title()
                    
                    structure[year].append({
                        "title": display_name,
                        "file": f"data/{year}/{album_slug}.json"
                    })

    # Save as a nested JSON
    with open(DATA_DIR / "albums_list.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2)

    # Build Nested HTML Menu
    menu_html = '<a onclick="showHome()">HOME</a>\n'
    for year in sorted(structure.keys(), reverse=True):
        menu_html += f'<div class="menu-year" onclick="toggleYear(\'year-{year}\')">{year} ▼</div>\n'
        menu_html += f'<div id="year-{year}" class="menu-albums" style="display:none;">\n'
        for album in structure[year]:
            menu_html += f'  <a onclick="loadAlbum(\'{album["file"]}\')">{album["title"]}</a>\n'
        menu_html += '</div>\n'
    
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        f.write(menu_html)

def rename_album():
    """Renames an album within a year"""
    year = input("Enter the YEAR of the album (e.g. 2025): ").strip()
    old_name = input("Enter current album name: ").strip().lower().replace(" ", "_")
    
    old_folder = IMAGE_ROOT / year / old_name
    old_json = DATA_DIR / year / f"{old_name}.json"

    if not old_folder.exists():
        print(f"❌ Error: Folder '{old_folder}' not found.")
        return

    new_name = input("Enter the NEW name: ").strip().lower().replace(" ", "_")
    new_folder = IMAGE_ROOT / year / new_name
    new_json = DATA_DIR / year / f"{new_name}.json"

    if new_folder.exists():
        print(f"❌ Error: '{new_name}' already exists in {year}.")
        return

    try:
        shutil.move(str(old_folder), str(new_folder))
        if old_json.exists():
            shutil.move(str(old_json), str(new_json))
        print(f"✅ Renamed to '{new_name}'")
    except Exception as e:
        print(f"❌ Rename failed: {e}")

def process_images():
    """Adds images to a Year/Album structure"""
    
    # 1. Ask for Year AND Album
    year = input("Enter YEAR (e.g. 2025): ").strip()
    if not year: year = "uncategorized"
    
    album_input = input("Enter album name: ").strip()
    if not album_input: return
    album_slug = album_input.lower().replace(" ", "_").replace("'", "")

    # 2. Setup Nested Paths
    ALBUM_ROOT = IMAGE_ROOT / year / album_slug
    ALBUM_THUMBS = ALBUM_ROOT / "thumbs"
    
    DATA_YEAR_DIR = DATA_DIR / year
    ALBUM_JSON = DATA_YEAR_DIR / f"{album_slug}.json"

    # 3. Create Directories
    ALBUM_THUMBS.mkdir(parents=True, exist_ok=True)
    DATA_YEAR_DIR.mkdir(parents=True, exist_ok=True)

    # 4. Load existing data
    images_data = []
    if ALBUM_JSON.exists():
        with open(ALBUM_JSON, "r", encoding="utf-8") as f:
            images_data = json.load(f)

    def get_next_idx(data):
        existing = [int(i['file'].split('_')[1].split('.')[0]) for i in data if 'photo_' in i['file']]
        return max(existing, default=0) + 1

    files = sorted([f for f in INCOMING_DIR.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS])
    
    if not files:
        print(f"No new images found in {INCOMING_DIR}")
        return
    
    for img_path in files:
        idx = get_next_idx(images_data)
        new_name = f"photo_{idx:03d}.jpg"
        print(f"Processing {img_path.name}...")
        
        try:
            with Image.open(img_path) as img:
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                
                img.thumbnail(THUMB_MAX_SIZE)
                img.convert("RGB").save(ALBUM_THUMBS / new_name, "JPEG", quality=85)
                
            print(f"  Uploading to ImgBB...")
            full_res_url = upload_to_imgbb(img_path)
            
            if full_res_url:
                images_data.append({
                    "file": new_name, 
                    "full_url": full_res_url, 
                    "width": width, 
                    "height": height
                })
                img_path.unlink()
                print(f"  ✅ Success: {new_name}")
            else:
                print(f"  ⚠️ Upload failed, skipping.")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    with open(ALBUM_JSON, "w", encoding="utf-8") as f:
        json.dump(images_data, f, indent=2)

if __name__ == "__main__":
    print("--- Gallery Manager (Nested Folders) ---")
    print("[1] Add new photos")
    print("[2] Rename an album")
    print("[3] Just refresh menu")
    
    choice = input("\nChoose option: ").strip()

    if choice == "1":
        process_images()
        rebuild_master_files()
    elif choice == "2":
        rename_album()
        rebuild_master_files()
    elif choice == "3":
        rebuild_master_files()