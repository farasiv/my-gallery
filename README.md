# My Personal Gallery

A personal photo gallery built with vanilla HTML, CSS, and JavaScript, hosted on GitHub Pages. Photos are organized by year and album. Full-resolution images are hosted on [imgbb](https://imgbb.com/); thumbnails are stored in the repository.

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
    └── swap_images.py          # Reorder photos within an album
```

Each album JSON file contains an array of photo entries:

```json
[
  {
    "file": "photo_001.jpg",
    "full_url": "https://i.ibb.co/...",
    "width": 3000,
    "height": 4000
  }
]
```

- `file` — the thumbnail filename, stored locally under `images/year/album/thumbs/`
- `full_url` — the full-resolution image hosted on imgbb, used by the lightbox
- `width` / `height` — original image dimensions, required by PhotoSwipe

---

## Adding New Photos

1. Drop your photos into the `incoming/` folder at the repo root.
2. Run the tool:
   ```bash
   cd tools
   python prepare_album.py
   ```
3. Select or create a year and album when prompted.
4. The script will:
   - Generate thumbnails and save them to `images/year/album/thumbs/`
   - Upload the full-resolution originals to imgbb
   - Update the album's JSON file
   - Rebuild `menu.html` and `data/albums_list.json`
5. Commit and push the changes to GitHub.

---

## Deleting Photos or Albums

```bash
cd tools
python delete_manager.py
```

- Option `1` — delete specific photos from an album by number
- Option `2` — delete an entire album and all its files

After deleting, the script updates the JSON automatically. Run `prepare_album.py` option `3` (Just refresh menu) afterwards to rebuild `menu.html`.

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

By default, Live Server returns a white screen when you visit a deep URL like `http://127.0.0.1:5500/2025/eventide` directly, because it looks for a real folder at that path. To fix this, add the following to your `.vscode/settings.json` (create the file if it doesn't exist):

```json
{
    "liveServer.settings.file": "/index.html"
}
```

This tells Live Server to always serve `index.html` for unknown paths, the same way `404.html` handles it on GitHub Pages.

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
| [imgbb](https://imgbb.com/) | — | Full-resolution image hosting |

All JavaScript dependencies are bundled locally — no CDN, no npm, no build tools required.
