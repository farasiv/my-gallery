import json
import requests
import shutil
import base64
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

DATA_DIR.mkdir(exist_ok=True)
IMAGE_ROOT.mkdir(exist_ok=True)
INCOMING_DIR.mkdir(exist_ok=True)
# ----------------------------------------

def upload_to_imgbb(image_path):
    """Uploads an image to ImgBB and returns the direct display URL"""
    url = "https://api.imgbb.com/1/upload"
    try:
        with open(image_path, "rb") as file:
            # Convert image to base64 to prevent "Invalid URL" errors
            base64_image = base64.b64encode(file.read())
            
            payload = {
                "key": API_KEY,
                "image": base64_image,
            }
            # Send the request
            res = requests.post(url, data=payload)
            
            if res.status_code == 200:
                json_data = res.json()
                # 'url' is the direct link to the image file
                return json_data['data']['url']
            else:
                print(f"❌ ImgBB Upload Error: {res.text}")
                return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

def rebuild_master_files():
    """Scans folders to update menu.html and data/albums_list.json"""
    print("\nRefreshing master files...")
    # We look for folders that have a 'thumbs' directory
    albums = [d.name for d in IMAGE_ROOT.iterdir() if d.is_dir() and (d / "thumbs").exists()]
    albums.sort() 

    with open(DATA_DIR / "albums_list.json", "w", encoding="utf-8") as f:
        json.dump(albums, f, indent=2)

    menu_html = '<a onclick="showHome()">HOME</a>\n'
    for alb in albums:
        display_name = alb.replace('_', ' ').upper()
        menu_html += f'<a onclick="loadAlbum(\'{alb}\')">{display_name}</a>\n'
    
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        f.write(menu_html)
    
    print("✅ Done: menu.html and albums_list.json are up to date.")

def rename_album():
    """Renames an existing album folder and its JSON file"""
    old_name = input("Enter the CURRENT album folder name: ").strip().lower().replace(" ", "_")
    old_folder = IMAGE_ROOT / old_name
    old_json = DATA_DIR / f"{old_name}.json"

    if not old_folder.exists():
        print(f"❌ Error: Folder 'images/{old_name}' not found.")
        return

    new_name = input("Enter the NEW name: ").strip().lower().replace(" ", "_")
    new_folder = IMAGE_ROOT / new_name
    new_json = DATA_DIR / f"{new_name}.json"

    if new_folder.exists():
        print(f"❌ Error: A folder named '{new_name}' already exists.")
        return

    try:
        shutil.move(str(old_folder), str(new_folder))
        if old_json.exists():
            shutil.move(str(old_json), str(new_json))
        print(f"✅ Successfully renamed '{old_name}' to '{new_name}'")
    except Exception as e:
        print(f"❌ Rename failed: {e}")

def process_images():
    """Adds new images from incoming to an album, uploads full to ImgBB"""
    album_name = input("Enter album name to add photos to: ").strip().lower().replace(" ", "_").replace("'", "")
    if not album_name: return

    ALBUM_THUMBS = IMAGE_ROOT / album_name / "thumbs"
    ALBUM_JSON = DATA_DIR / f"{album_name}.json"

    ALBUM_THUMBS.mkdir(parents=True, exist_ok=True)

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
            # 1. Open and fix rotation
            with Image.open(img_path) as img:
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                
                # 2. Create and save Local Thumbnail
                img.thumbnail(THUMB_MAX_SIZE)
                img.convert("RGB").save(ALBUM_THUMBS / new_name, "JPEG", quality=85)
                
            # 3. Upload Original to ImgBB
            print(f"  Uploading full-res to ImgBB...")
            full_res_url = upload_to_imgbb(img_path)
            
            if full_res_url:
                images_data.append({
                    "file": new_name, 
                    "full_url": full_res_url, 
                    "width": width, 
                    "height": height
                })
                img_path.unlink() # Delete from incoming only if upload worked
                print(f"  ✅ Success: {new_name}")
            else:
                print(f"  ⚠️ Skipping {img_path.name} due to upload failure.")

        except Exception as e:
            print(f"  ❌ Error processing {img_path.name}: {e}")

    with open(ALBUM_JSON, "w", encoding="utf-8") as f:
        json.dump(images_data, f, indent=2)

if __name__ == "__main__":
    print("--- Gallery Manager (ImgBB Version) ---")
    print("[1] Add new photos (Upload to ImgBB)")
    print("[2] Rename an existing album")
    print("[3] Just refresh menu/list")
    
    choice = input("\nChoose an option: ").strip()

    if choice == "1":
        process_images()
    elif choice == "2":
        rename_album()
    
    rebuild_master_files()