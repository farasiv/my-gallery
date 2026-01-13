let lightbox;

// Utility to handle menu visibility
function toggleYear(yearId, forceState) {
    const element = document.getElementById(yearId);
    if (!element) return;

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

// 1. Load the menu links and FORCE UPPERCASE
function loadMenu() {
    fetch('./menu.html')
        .then(response => response.text())
        .then(data => {
            const menuContainer = document.getElementById('album-menu');
            menuContainer.innerHTML = data;
            // Beautifier: Force all dropdown links to be uppercase
            menuContainer.querySelectorAll('a').forEach(a => {
                a.style.textTransform = 'uppercase';
            });
        })
        .catch(err => console.error("Menu failed to load:", err));
}

// 2. HOME SCREEN: Forced horizontal grid
async function showHome() {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');

    document.querySelectorAll('.menu-albums').forEach(el => el.style.display = 'none');

    homeScreen.style.display = 'grid';
    // Forced Horizontal Alignment: repeat as many columns as fit
    homeScreen.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
    homeScreen.style.gap = '20px'; 
    
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

            const firstAlbum = albumsInYear[0];
            const albRes = await fetch(firstAlbum.file);
            const images = await albRes.json();
            
            const slug = firstAlbum.file.split('/').pop().replace('.json', '');
            const thumbPath = `images/${year}/${slug}/thumbs/${images[0].file}`;

            const card = document.createElement('div');
            card.className = 'album-card';
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
    }
}

// 3. YEAR VIEW: Forced horizontal grid
async function loadYearView(year) {
    const homeScreen = document.getElementById('home-screen');
    const galleryView = document.getElementById('gallery-view');
    
    homeScreen.style.display = 'grid';
    homeScreen.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
    galleryView.style.display = 'none';
    
    homeScreen.innerHTML = 'Loading albums...';
    toggleYear(`year-${year}`, 'close'); 

    try {
        const response = await fetch('./data/albums_list.json');
        const structure = await response.json();
        const albums = structure[year];

        homeScreen.innerHTML = ''; 
        
        for (const album of albums) {
            const albRes = await fetch(album.file);
            const images = await albRes.json();
            const albumSlug = album.file.split('/').pop().replace('.json', '');
            
            const card = document.createElement('div');
            card.className = 'album-card'; 
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
        console.error(err);
    }
}

// 4. PHOTO VIEW: Added Back Button
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
    
    // BEAUTIFIER: Adding the Back Button (Arrow)
    title.innerHTML = `
        <span class="back-arrow" onclick="loadYearView('${year}')" style="cursor:pointer; margin-right:13px; opacity:0.7; font-size: 1.35em; font-weight: 900;">←</span>
        ${slug.toUpperCase().replace(/_/g, ' ')}
    `;

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


window.onload = () => {
    loadMenu();
    showHome();
};