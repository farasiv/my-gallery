let lightbox;

// Utility to handle menu visibility
function toggleYear(yearId, forceState) {
    const element = document.getElementById(yearId);
    if (!element) return;

    // Close all other menus
    document.querySelectorAll('.menu-albums').forEach(el => {
        if (el.id !== yearId) el.style.display = 'none';
    });

    if (forceState === 'open') {
        element.style.display = 'block';
    } else if (forceState === 'close') {
        element.style.display = 'none';
    } else {
        element.style.display = element.style.display === 'block' ? 'none' : 'block';
    }
}

// 1. Load the menu links from menu.html
function loadMenu() {
    fetch('./menu.html')
        .then(response => response.text())
        .then(data => {
            document.getElementById('album-menu').innerHTML = data;
        })
        .catch(err => console.error("Menu failed to load:", err));
}

// 2. HOME SCREEN: Shows Year Folders
async function showHome() {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');

    // Close all menus when going home
    document.querySelectorAll('.menu-albums').forEach(el => el.style.display = 'none');

    homeScreen.style.display = 'grid';
    galleryView.style.display = 'none';
    homeScreen.innerHTML = '<p>Loading years...</p>';

    try {
        const response = await fetch('./data/albums_list.json');
        const structure = await response.json(); 
        
        homeScreen.innerHTML = ''; 

        const years = Object.keys(structure).sort((a, b) => b - a);

        for (const year of years) {
            const albumsInYear = structure[year];
            if (albumsInYear.length === 0) continue;

            // Get preview from the first album
            const firstAlbum = albumsInYear[0];
            const albRes = await fetch(firstAlbum.file);
            const images = await albRes.json();
            
            const slug = firstAlbum.file.split('/').pop().replace('.json', '');
            const thumbPath = `images/${year}/${slug}/thumbs/${images[0].file}`;

            const card = document.createElement('div');
            card.className = 'album-card year-card';
            card.onclick = () => loadYearView(year); // Clicking folder shows albums
            
            card.innerHTML = `
                <img src="${thumbPath}" loading="lazy">
                <div class="album-info">
                    <h2>${year}</h2>
                    <span>${albumsInYear.length} Folders</span>
                </div>
            `;
            homeScreen.appendChild(card);
        }
    } catch (e) {
        homeScreen.innerHTML = '<p>Error loading years.</p>';
        console.error(e);
    }
}

// 3. YEAR VIEW: Shows Albums inside that year (Card Grid)
async function loadYearView(year) {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');
    
    homeScreen.style.display = 'none';
    galleryView.style.display = 'block';
    
    const gallery = document.getElementById('gallery');
    const title = document.getElementById('album-title');
    
    title.innerText = `Year ${year}`;
    gallery.innerHTML = 'Loading albums...';

    // Keep dropdown CLOSED when viewing the album grid
    toggleYear(`year-${year}`, 'close'); 

    try {
        const response = await fetch('./data/albums_list.json');
        const structure = await response.json();
        const albums = structure[year];

        gallery.innerHTML = ''; 
        
        for (const album of albums) {
            const albRes = await fetch(album.file);
            const images = await albRes.json();
            const albumSlug = album.file.split('/').pop().replace('.json', '');
            
            const card = document.createElement('div');
            card.className = 'album-card'; 
            card.onclick = () => loadAlbum(album.file); // Clicking album shows photos
            
            card.innerHTML = `
                <img src="images/${year}/${albumSlug}/thumbs/${images[0].file}" loading="lazy">
                <div class="album-info">
                    <h2>${album.title.toUpperCase()}</h2>
                    <span>${images.length} Photos</span>
                </div>
            `;
            gallery.appendChild(card);
        }
    } catch (err) {
        console.error(err);
    }
}

// 4. PHOTO VIEW: Shows the actual photos and opens the dropdown
function loadAlbum(jsonPath) {
    document.getElementById('home-screen').style.display = 'none';
    document.getElementById('gallery-view').style.display = 'block';

    const gallery = document.getElementById('gallery');
    const title = document.getElementById('album-title');
    gallery.innerHTML = 'Loading photos...';

    const parts = jsonPath.split('/');
    const year = parts[1];
    const slug = parts[2].replace('.json', '');
    
    title.innerText = slug.toUpperCase().replace(/_/g, ' ');

    // OPEN the dropdown now that we are looking at specific photos
    toggleYear(`year-${year}`, 'open');

    fetch(`${jsonPath}?v=${new Date().getTime()}`)
        .then(response => response.json())
        .then(images => {
            gallery.innerHTML = '';

            images.forEach(img => {
                const link = document.createElement('a');
                link.href = img.full_url; 
                link.dataset.pswpWidth = img.width;
                link.dataset.pswpHeight = img.height;
                link.target = "_blank";
                link.rel = "noopener noreferrer";

                const image = document.createElement('img');
                image.src = `images/${year}/${slug}/thumbs/${img.file}`;
                image.loading = 'lazy';

                link.appendChild(image);
                gallery.appendChild(link);
            });

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
        .catch(err => console.error(err));
}

// 5. Initial startup
window.onload = () => {
    loadMenu();
    showHome();
};