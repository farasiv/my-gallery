import json
import requests
import base64
import io
import time
from pathlib import Path
from PIL import Image

# ---------------- CONFIG ----------------
API_KEY = "94761cb08cb48333e177d234749f7521"
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

WEB_MAX_SIZE = (1800, 1800)
# ----------------------------------------

def download_image(url):
    """Downloads image from URL and returns raw bytes or None."""
    try:
        res = requests.get(url, timeout=60)
        if res.status_code == 200:
            return res.content
        else:
            print(f"    ⚠️  Download failed — HTTP {res.status_code}")
            return None
    except requests.exceptions.Timeout:
        print(f"    ⚠️  Download timed out")
        return None
    except Exception as e:
        print(f"    ⚠️  Download error: {e}")
        return None

def resize_to_web(image_bytes):
    """Resizes image to max 1800px on long edge, returns JPEG bytes or None."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert("RGB")
            img.thumbnail(WEB_MAX_SIZE)
            out = io.BytesIO()
            img.save(out, "JPEG", quality=85)
            return out.getvalue()
    except Exception as e:
        print(f"    ⚠️  Resize failed: {e}")
        return None

def upload_to_imgbb(image_bytes):
    """Uploads image bytes to imgbb and returns URL or None."""
    url = "https://api.imgbb.com/1/upload"
    try:
        base64_image = base64.b64encode(image_bytes)
        payload = {"key": API_KEY, "image": base64_image}
        res = requests.post(url, data=payload, timeout=60)
        if res.status_code == 200:
            return res.json()['data']['url']
        else:
            error_msg = res.json().get('error', {}).get('message', res.text)
            print(f"    ⚠️  Upload failed — imgbb error {res.status_code}: {error_msg}")
            return None
    except requests.exceptions.Timeout:
        print(f"    ⚠️  Upload timed out")
        return None
    except Exception as e:
        print(f"    ⚠️  Upload error: {e}")
        return None

def process_album(json_path):
    """Processes a single album JSON file — adds web_url to entries that don't have it."""
    with open(json_path, "r", encoding="utf-8") as f:
        images_data = json.load(f)

    needs_processing = [i for i, item in enumerate(images_data) if "web_url" not in item and "full_url" in item]

    if not needs_processing:
        return 0, 0

    print(f"\n  📁 {json_path.relative_to(BASE_DIR)} — {len(needs_processing)} image(s) to process")

    success = 0
    failed = 0

    for i in needs_processing:
        item = images_data[i]
        print(f"    Processing {item['file']}...")

        # Step 1: Download original
        image_bytes = download_image(item['full_url'])
        if not image_bytes:
            print(f"    ❌ Skipping {item['file']} — could not download")
            failed += 1
            continue

        # Step 2: Resize to 1800px
        web_bytes = resize_to_web(image_bytes)
        if not web_bytes:
            print(f"    ❌ Skipping {item['file']} — could not resize")
            failed += 1
            continue

        # Step 3: Upload web version to imgbb
        web_url = upload_to_imgbb(web_bytes)
        if not web_url:
            print(f"    ❌ Skipping {item['file']} — could not upload")
            failed += 1
            continue

        # Step 4: Save web_url to JSON entry
        images_data[i]['web_url'] = web_url

        # Save after every successful upload so progress is never lost
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(images_data, f, indent=2)

        print(f"    ✅ {item['file']}")
        success += 1

        # Small delay to avoid hammering imgbb
        time.sleep(0.5)

    return success, failed

def run_migration():
    print("=" * 60)
    print("  Gallery web_url Migration")
    print("  Adds 1800px web versions to all existing album entries")
    print("=" * 60)

    # Find all album JSON files (skip albums_list.json)
    json_files = sorted([
        p for p in DATA_DIR.rglob("*.json")
        if p.name != "albums_list.json"
    ])

    if not json_files:
        print("\nNo album JSON files found.")
        return

    total_success = 0
    total_failed = 0
    skipped_albums = 0

    for json_path in json_files:
        success, failed = process_album(json_path)
        if success == 0 and failed == 0:
            skipped_albums += 1
        total_success += success
        total_failed += failed

    print("\n" + "=" * 60)
    print(f"  Migration complete")
    print(f"  ✅ {total_success} images processed successfully")
    if total_failed > 0:
        print(f"  ❌ {total_failed} images failed — re-run to retry")
    if skipped_albums > 0:
        print(f"  ⏭️  {skipped_albums} albums already up to date")
    print("=" * 60)

if __name__ == "__main__":
    run_migration()
