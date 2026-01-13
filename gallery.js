let lightbox;

// 1. Load the menu links from menu.html
function loadMenu() {
    fetch('./menu.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('album-menu').innerHTML = data;
        })
        .catch(err => console.error("Menu failed to load:", err));
}

// 2. Build the Home Screen Grid using the master list
async function showHome() {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');
    
    homeScreen.style.display = 'grid';
    galleryView.style.display = 'none';
    homeScreen.innerHTML = '<p>Loading albums...</p>';

    try {
        const response = await fetch('./data/albums_list.json');
        const albumIds = await response.json();
        
        homeScreen.innerHTML = ''; 

        for (const id of albumIds) {
            const albRes = await fetch(`./data/${id}.json`);
            const images = await albRes.json();
            
            if (images.length > 0) {
                const coverImg = images[0].file;
                const title = id.toUpperCase().replace(/_/g, ' ');

                const card = document.createElement('div');
                card.className = 'album-card';
                card.onclick = () => loadAlbum(id);
                card.innerHTML = `
                    <img src="images/${id}/thumbs/${coverImg}" loading="lazy">
                    <div class="album-info">
                        <h2>${title}</h2>
                        <span>${images.length} Photos</span>
                    </div>
                `;
                homeScreen.appendChild(card);
            }
        }
    } catch (e) {
        homeScreen.innerHTML = '<p>No albums found. Run your Python script!</p>';
        console.error("Home screen error:", e);
    }
}

// 3. Load Album with ImgBB Support
function loadAlbum(albumName) {
    // UI Transitions
    document.getElementById('home-screen').style.display = 'none';
    document.getElementById('gallery-view').style.display = 'block';

    const gallery = document.getElementById('gallery');
    const title = document.getElementById('album-title');
    
    title.innerText = albumName.toUpperCase().replace(/_/g, ' ');
    gallery.innerHTML = 'Loading photos...';

    // Fetch the album JSON
    fetch(`./data/${albumName}.json?v=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) throw new Error(`File not found: ${albumName}.json`);
            return response.json();
        })
        .then(images => {
            gallery.innerHTML = '';

            images.forEach(img => {
                const link = document.createElement('a');
                
                // CRITICAL UPDATE: Pointing to the ImgBB URL
                link.href = img.full_url; 
                
                link.dataset.pswpWidth = img.width;
                link.dataset.pswpHeight = img.height;
                
                // Helps with external link permissions
                link.target = "_blank";
                link.rel = "noopener noreferrer";

                const image = document.createElement('img');
                // Thumbs remain local in your 'images/[album]/thumbs' folder
                image.src = `images/${albumName}/thumbs/${img.file}`;
                image.loading = 'lazy';

                link.appendChild(image);
                gallery.appendChild(link);
            });

            // Initialize PhotoSwipe Lightbox
            if (lightbox) lightbox.destroy();
            
            if (typeof PhotoSwipeLightbox !== 'undefined') {
                lightbox = new PhotoSwipeLightbox({
                    gallery: '#gallery',
                    children: 'a',
                    pswpModule: PhotoSwipe 
                });
                lightbox.init();
            }
        })
        .catch(err => {
            gallery.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
            console.error(err);
        });
}

// 4. Initial startup
window.onload = () => {
    loadMenu();
    showHome();
};