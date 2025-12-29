fetch('images.json')
  .then(response => response.json())
  .then(images => {
    const gallery = document.getElementById('gallery');

    images.forEach(img => {
      const link = document.createElement('a');

      // FULL IMAGE
      link.href = `images/full/${img.file}`;

      // ⚠️ THESE TWO LINES ARE CRITICAL
      link.dataset.pswpWidth = img.width;
      link.dataset.pswpHeight = img.height;

      // THUMBNAIL
      const image = document.createElement('img');
      image.src = `images/thumbs/${img.file}`;
      image.loading = 'lazy';

      link.appendChild(image);
      gallery.appendChild(link);
    });

    const lightbox = new PhotoSwipeLightbox({
      gallery: '#gallery',
      children: 'a',
      pswpModule: PhotoSwipe,
      bgOpacity: 0.9,
      showHideAnimationType: 'fade'
    });

    lightbox.init();
  });
