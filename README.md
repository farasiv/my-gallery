# My Personal Gallery

A personal photo gallery built with vanilla HTML, CSS, and JavaScript, hosted on GitHub Pages. Photos are organized by year and album. Images are hosted on [imgbb](https://imgbb.com/); thumbnails are stored in the repository.

---

## How It Works

The gallery has three levels of navigation:

```
Home (years) → Year view (albums) → Album view (photos)
```

Each level has its own URL, so albums can be shared as direct links:

```
https://farasiv.github.io/my-gallery/              ← Home
https://farasiv.github.io/my-gallery/2025          ← Year
https://farasiv.github.io/my-gallery/2025/eventide ← Album
```

The browser back button works correctly at every level.

---

## How Images Are Stored

Each photo is uploaded to imgbb **twice** from a single processing run:

- `web_url` — resized to max 1800px on the long edge, JPEG quality 85. Used by the lightbox for fast loading.
- `full_url` — the original full-resolution file. Used by the download button.

Thumbnails (max 600px) are generated locally and stored in the repository under `images/`.

Each album JSON entry looks like this:

```json
[
  {
    "file": "photo_001.jpg",
    "web_url": "https://i.ibb.co/...",
    "full_url": "https://i.ibb.co/...",
    "width": 3000,
    "height": 4000
  }
]
```

- `file` — thumbnail filename, stored locally under `images/year/album/thumbs/`
- `web_url` — 1800px version on imgbb, used by PhotoSwipe lightbox
- `full_url` — original resolution on imgbb, used by download button
- `width` / `height` — original image dimensions, required by PhotoSwipe

---

## File Structure

```
my-gallery/
│
├── index.html                  # The single HTML page
├── gallery.js                  # All navigation and rendering logic
├── style.css                   # All styles
├── menu.html                   # Auto-generated navigation menu (do not edit manually)
├── 404.html                    # Handles direct URL visits on GitHub Pages
│
├── photoswipe.css              # PhotoSwipe lightbox styles
├── photoswipe-lightbox.umd.min.js
├── photoswipe.umd.min.js
│
├── data/
│   ├── albums_list.json        # Master index of all years and albums
│   ├── 2025/
│   │   ├── eventide.json       # Photo list for each album
│   │   └── spring_2025.json
│   └── 2026/
│       └── winter_2026.json
│
├── images/
│   ├── 2025/
│   │   ├── eventide/
│   │   │   └── thumbs/         # Local thumbnails (max 600×600px)
│   │   │       ├── photo_001.jpg
│   │   │       └── ...
│   │   └── spring_2025/
│   │       └── thumbs/
│   └── 2026/
│       └── winter_2026/
│           └── thumbs/
│
└── tools/
    ├── prepare_album.py        # Add new photos to an album
    ├── delete_manager.py       # Delete photos or entire albums
    ├── swap_images.py          # Reorder photos within an album
    └── resize_images.py        # Resize incoming images to max 4000px long edge
```

---

## Adding New Photos

1. Drop your photos into the `incoming/` folder at the repo root
2. (Optional) If any photos are very large, resize them first:
   ```bash
   cd tools
   python resize_images.py
   ```
3. Run the main tool:
   ```bash
   cd tools
   python prepare_album.py
   ```
4. Select or create a year and album when prompted
5. The script will:
   - Sanitize filenames (removes spaces and special characters)
   - Generate thumbnails saved to `images/year/album/thumbs/`
   - Upload a 1800px web version to imgbb (`web_url`)
   - Upload the full original to imgbb (`full_url`)
   - Save progress after every successful upload (safe to restart if interrupted)
   - Update the album's JSON file
   - Rebuild `menu.html` and `data/albums_list.json`
6. Commit and push the changes to GitHub

---

## If the Script Is Interrupted

The script saves progress after every successful image. If it crashes or you stop it mid-way, just run it again — it will skip already-processed images and continue from where it left off. Failed images are left in `incoming/` for you to retry.

---

## Deleting Photos or Albums

```bash
cd tools
python delete_manager.py
```

- Option `1` — delete specific photos from an album by number
- Option `2` — delete an entire album and all its files

After deleting, run `prepare_album.py` option `3` to rebuild the menu.

---

## Reordering Photos

```bash
cd tools
python swap_images.py
```

Select a year and album, then enter two photo numbers to swap their positions. The script re-indexes all filenames sequentially after the swap.

---

## Local Development

### Prerequisites

- Python 3.x with Pillow and Requests installed:
  ```bash
  pip install Pillow requests
  ```
- A local web server. The recommended option is the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension for VS Code.

### Setting Up Live Server for SPA Routing

By default, Live Server returns a white screen when you visit a deep URL like `http://127.0.0.1:5500/2025/eventide` directly. To fix this, add the following to your `.vscode/settings.json` (create the file if it doesn't exist):

```json
{
    "liveServer.settings.file": "/index.html"
}
```

### BASE_PATH Setting

At the top of `gallery.js` there is a single config variable:

```javascript
const BASE_PATH = '';             // ← local development
const BASE_PATH = '/my-gallery';  // ← GitHub Pages (production)
```

**Always set `BASE_PATH = ''` when developing locally, and set it back to `'/my-gallery'` before pushing to GitHub.** If you forget this, the gallery will show "Error loading years" on GitHub Pages.

### Workflow

1. Set `BASE_PATH = ''` in `gallery.js`
2. Open the project in VS Code and click **Go Live**
3. Navigate to `http://127.0.0.1:5500/`
4. Make your changes and test
5. Set `BASE_PATH = '/my-gallery'` in `gallery.js`
6. Commit and push

---

## Deployment

This project is hosted on **GitHub Pages** from the `main` branch. Every push to `main` automatically updates the live site at:

```
https://farasiv.github.io/my-gallery/
```

No build step is required — everything is plain HTML, CSS, and JavaScript.

---

## Dependencies

| Library | Version | Purpose |
|---|---|---|
| [PhotoSwipe](https://photoswipe.com/) | 5.4.4 | Lightbox / fullscreen photo viewer |
| [imgbb](https://imgbb.com/) | — | Image hosting (web and full resolution versions) |

All JavaScript dependencies are bundled locally — no CDN, no npm, no build tools required.
