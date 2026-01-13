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

    // Close all dropdowns when going home
    document.querySelectorAll('.menu-albums').forEach(el => el.style.display = 'none');

    homeScreen.style.display = 'grid'; // Ensure grid layout is active
    galleryView.style.display = 'none';
    homeScreen.innerHTML = '<p>Loading years...</p>';

    try {
        const response = await fetch('./data/albums_list.json');
        const structure = await response.json(); 
        
        homeScreen.innerHTML = ''; 

        // Sort years descending (2026, 2025...)
        const years = Object.keys(structure).sort((a, b) => b - a);

        for (const year of years) {
            const albumsInYear = structure[year];
            if (albumsInYear.length === 0) continue;

            // Get preview from the first album in that year
            const firstAlbum = albumsInYear[0];
            const albRes = await fetch(firstAlbum.file);
            const images = await albRes.json();
            
            const slug = firstAlbum.file.split('/').pop().replace('.json', '');
            const thumbPath = `images/${year}/${slug}/thumbs/${images[0].file}`;

            const card = document.createElement('div');
            card.className = 'album-card'; // Using the standard album-card class for spacing
            card.onclick = () => loadYearView(year);
            
            card.innerHTML = `
                <img src="${thumbPath}" loading="lazy">
                <div class="album-info">
                    <h2>${year}</h2>
                    <span>${albumsInYear.length} Albums</span>
                </div>
            `;
            homeScreen.appendChild(card);
        }
    } catch (e) {
        homeScreen.innerHTML = '<p>Error loading years.</p>';
        console.error(e);
    }
}

// 3. YEAR VIEW: Shows Albums inside that year
// FIX: We keep the 'home-screen' grid style so cards don't touch
async function loadYearView(year) {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');
    
    // UI Setup: We stay in the "Grid" mode
    homeScreen.style.display = 'grid'; 
    galleryView.style.display = 'none';
    homeScreen.innerHTML = '<p>Loading albums...</p>';

    // Close dropdown per hierarchy logic
    toggleYear(`year-${year}`, 'close'); 

    try {
        const response = await fetch('./data/albums_list.json');
        const structure = await response.json();
        const albums = structure[year]; // This array maintains the order from your JSON

        homeScreen.innerHTML = ''; 
        
        for (const album of albums) {
            const albRes = await fetch(album.file);
            const images = await albRes.json();
            const albumSlug = album.file.split('/').pop().replace('.json', '');
            
            const card = document.createElement('div');
            card.className = 'album-card'; // This class provides the padding/margins you like
            card.onclick = () => loadAlbum(album.file);
            
            card.innerHTML = `
                <img src="images/${year}/${albumSlug}/thumbs/${images[0].file}" loading="lazy">
                <div class="album-info">
                    <h2>${album.title.toUpperCase()}</h2>
                    <span>${images.length} Photos</span>
                </div>
            `;
            homeScreen.appendChild(card);
        }
    } catch (err) {
        homeScreen.innerHTML = '<p>Error loading albums.</p>';
        console.error(err);
    }
}

// 4. PHOTO VIEW: Shows individual photos
function loadAlbum(jsonPath) {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');

    homeScreen.style.display = 'none';
    galleryView.style.display = 'block';

    const gallery = document.getElementById('gallery');
    const title = document.getElementById('album-title');
    gallery.innerHTML = 'Loading photos...';

    const parts = jsonPath.split('/');
    const year = parts[1];
    const slug = parts[2].replace('.json', '');
    
    title.innerText = slug.toUpperCase().replace(/_/g, ' ');

    // Open the menu dropdown for the current year
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
        .catch(err => {
            gallery.innerHTML = '<p>Error loading photos.</p>';
            console.error(err);
        });
}

// 5. Initial startup
window.onload = () => {
    loadMenu();
    showHome();
};