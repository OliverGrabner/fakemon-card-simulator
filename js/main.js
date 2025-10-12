// List of generated card images
const cardImages = [
  'assets/images/generated_cards/generated_image_1.png',
  'assets/images/generated_cards/generated_image_1012.png',
  'assets/images/generated_cards/generated_image_1046.png',
  'assets/images/generated_cards/generated_image_1047.png',
  'assets/images/generated_cards/generated_image_1048.png',
  'assets/images/generated_cards/generated_image_1052.png',
  'assets/images/generated_cards/generated_image_1078.png',
  'assets/images/generated_cards/generated_image_109.png',
  'assets/images/generated_cards/generated_image_1106.png',
  'assets/images/generated_cards/generated_image_117.png',
  'assets/images/generated_cards/generated_image_122.png',
  'assets/images/generated_cards/generated_image_19.png',
  'assets/images/generated_cards/generated_image_224.png',
  'assets/images/generated_cards/generated_image_247.png',
  'assets/images/generated_cards/generated_image_256.png',
  'assets/images/generated_cards/generated_image_257.png',
  'assets/images/generated_cards/generated_image_27.png',
  'assets/images/generated_cards/generated_image_276.png',
  'assets/images/generated_cards/generated_image_279.png',
  'assets/images/generated_cards/generated_image_290.png',
  'assets/images/generated_cards/generated_image_291.png',
  'assets/images/generated_cards/generated_image_293.png',
  'assets/images/generated_cards/generated_image_301.png',
  'assets/images/generated_cards/generated_image_302.png',
  'assets/images/generated_cards/generated_image_305.png',
  'assets/images/generated_cards/generated_image_307.png',
  'assets/images/generated_cards/generated_image_319.png',
  'assets/images/generated_cards/generated_image_328.png',
  'assets/images/generated_cards/generated_image_336.png',
  'assets/images/generated_cards/generated_image_53.png',
  'assets/images/generated_cards/generated_image_63.png',
  'assets/images/generated_cards/generated_image_7.png',
  'assets/images/generated_cards/generated_image_78.png',
  'assets/images/generated_cards/generated_image_8.png',
  'assets/images/generated_cards/generated_image_83.png',
  'assets/images/generated_cards/generated_image_86.png',
  'assets/images/generated_cards/generated_image_95.png'
];

/* 
   Weighted Rarity Selection:
   Common: 70%
   Uncommon: 15%
   Rare: 8%
   Epic: 6%
   Legendary: 1%
*/
function getRandomRarity() {
  const rand = Math.random() * 100;
  if (rand < 70) return 'Common';
  else if (rand < 85) return 'Uncommon';
  else if (rand < 93) return 'Rare';
  else if (rand < 99) return 'Epic';
  else return 'Legendary';
}

// Helper: pick a random element from an array
function getRandomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// Get a random card object with image and weighted rarity
function getRandomCard() {
  return {
    image: getRandomElement(cardImages),
    rarity: getRandomRarity()
  };
}

// Generate a pack of cards (default: 10)
function generateDailyPack(packSize = 10) {
  const packContainer = document.querySelector('.card-container');
  if (!packContainer) return;
  packContainer.innerHTML = '';

  for (let i = 0; i < packSize; i++) {
    const cardData = getRandomCard();
    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card');
    cardDiv.setAttribute('data-rarity', cardData.rarity.toLowerCase());
    cardDiv.innerHTML = `
      <div class="card-inner">
        <div class="card-front">
          <img src="assets/images/card-back.png" alt="Card Back">
        </div>
        <div class="card-back">
          <img src="${cardData.image}" alt="Generated Card">
          <div class="rarity-label">${cardData.rarity}</div>
        </div>
      </div>
      <div class="favorite-icon" title="Favorite this card">&#10084;</div>
    `;
    packContainer.appendChild(cardDiv);
  }
  attachCardEventListeners();
}

/* Tilt effect applied to a card.
   We now check if the card itself has the 'flip' class, rather than cardInner.
*/
function attachTiltEffect(card) {
  const cardInner = card.querySelector('.card-inner');
  
  card.addEventListener('mousemove', function(e) {
    cardInner.style.transition = 'transform 0.6s ease-out';
    const rect = card.getBoundingClientRect();
    const offsetX = e.clientX - rect.left;
    const offsetY = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const deltaX = offsetX - centerX;
    const deltaY = offsetY - centerY;
    const percentX = deltaX / centerX;
    const percentY = deltaY / centerY;
    const maxTilt = 25;
    const tiltX = -percentY * maxTilt;
    const tiltY = percentX * maxTilt;
    
    // If the .card is flipped, rotateY(180deg) first
    let transformString = card.classList.contains('flip') ? 'rotateY(180deg) ' : '';
    transformString += `rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    cardInner.style.transform = transformString;
  });

  card.addEventListener('mouseleave', function() {
    cardInner.style.transition = 'transform 0.6s ease-out';
    // If the .card is flipped, revert to rotateY(180deg), otherwise 0
    if (card.classList.contains('flip')) {
      cardInner.style.transform = 'rotateY(180deg)';
    } else {
      cardInner.style.transform = 'rotateX(0deg) rotateY(0deg)';
    }
  });
}

/* Attach event listeners for tilt, hover (scale), flip, and favorite.
   For cards with the "favorited-card" class (favorites page), we do not attach the flip (click) event,
   so they remain in the revealed state.
*/
function attachCardEventListeners() {
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    // Hover scale effect (applies to all cards)
    card.addEventListener('mouseenter', function() {
      card.style.transition = 'transform 0.3s ease';
      card.style.transform = 'scale(1.1)';
    });
    card.addEventListener('mouseleave', function() {
      card.style.transition = 'transform 0.3s ease';
      card.style.transform = 'scale(1)';
    });

    // Only attach flip event for non-favorites cards
    if (!card.classList.contains('favorited-card')) {
      card.addEventListener('click', function(e) {
        if (e.target.classList.contains('favorite-icon')) return;
        
        // Toggle the flip class on the .card itself (not cardInner)
        card.classList.toggle('flip');
        const cardInner = card.querySelector('.card-inner');
        
        if (card.classList.contains('flip')) {
          cardInner.style.transform = 'rotateY(180deg)';
        } else {
          cardInner.style.transform = 'rotateX(0deg) rotateY(0deg)';
        }
      });
    }
    // Attach tilt effect for all cards
    attachTiltEffect(card);
  });

  // Attach favorite icon functionality for all cards
  const favoriteIcons = document.querySelectorAll('.favorite-icon');
  favoriteIcons.forEach(icon => {
    icon.addEventListener('click', function(e) {
      e.stopPropagation();
      icon.classList.toggle('favorited');
      const cardElement = icon.closest('.card');
      const cardData = {
        imageSrc: cardElement.querySelector('.card-back img').src,
        rarity: cardElement.getAttribute('data-rarity')
      };
      toggleFavorite(cardData);
    });
  });
}

/* Manage favorites using localStorage.
   toggleFavorite() adds or removes the card from favorites.
*/
function toggleFavorite(cardData) {
  let favorites = JSON.parse(localStorage.getItem('favorites')) || [];
  const index = favorites.findIndex(fav => fav.imageSrc === cardData.imageSrc);
  if (index >= 0) {
    favorites.splice(index, 1);
  } else {
    favorites.push(cardData);
  }
  localStorage.setItem('favorites', JSON.stringify(favorites));
  
  // If on the favorites page, reload favorites
  if (document.getElementById('favorites-container')) {
    loadFavorites();
  }
}

/* Load favorites into the favorites container.
   For each favorite card, we build a card with the "favorited-card" class,
   force the card to show the generated side by default,
   and then attach the same event listeners (for tilt, hover, and unfavoriting).
*/
function loadFavorites() {
  const favoritesContainer = document.getElementById('favorites-container');
  favoritesContainer.innerHTML = "";
  let favorites = JSON.parse(localStorage.getItem('favorites')) || [];
  if (favorites.length === 0) {
    favoritesContainer.innerHTML = "<p>No favorites yet. Click on the heart icon to favorite a card!</p>";
    return;
  }
  favorites.forEach(cardData => {
    const card = document.createElement('div');
    card.className = 'card favorited-card flip'; // "flip" ensures the art side (card-back) is visible
    card.setAttribute('data-rarity', cardData.rarity.toLowerCase());
    
    card.innerHTML = `
      <div class="card-inner">
        <div class="card-front">
          <img src="assets/images/card-back.png" alt="Card Back">
        </div>
        <div class="card-back">
          <img src="${cardData.imageSrc}" alt="Favorited Card">
          <div class="rarity-label">${cardData.rarity}</div>
        </div>
      </div>
      <div class="favorite-icon favorited" title="Unfavorite">&#10084;</div>
    `;
    favoritesContainer.appendChild(card);
  });
  // Attach tilt, hover, and favorite events to the newly added favorites.
  attachCardEventListeners();
}

// Card Explorer Dropdown
function setupCardExplorer() {
  const toggleBtn = document.getElementById('explorer-toggle');
  const explorerContent = document.getElementById('explorer-content');
  const explorerGrid = document.querySelector('.explorer-grid');

  if (!toggleBtn || !explorerContent || !explorerGrid) return;

  // Toggle dropdown
  toggleBtn.addEventListener('click', function() {
    toggleBtn.classList.toggle('active');
    explorerContent.classList.toggle('open');
  });

  // Load all generated cards into the explorer
  cardImages.forEach(imagePath => {
    const img = document.createElement('img');
    img.src = imagePath;
    img.alt = 'Generated Card';
    img.loading = 'lazy';
    explorerGrid.appendChild(img);
  });
}

// Single DOMContentLoaded event to initialize everything
document.addEventListener("DOMContentLoaded", () => {
  // If we're on the game page, generate a new pack.
  if (document.querySelector('.card-container')) {
    generateDailyPack();
  }
  // If we're on the favorites page, load favorites.
  if (document.getElementById('favorites-container')) {
    loadFavorites();
  }

  // Attach event listener to "Open Another Pack" button (if on game page)
  const openAnotherBtn = document.getElementById('open-another');
  if (openAnotherBtn) {
    openAnotherBtn.addEventListener('click', function() {
      generateDailyPack();
      document.querySelector('.card-container').scrollIntoView({ behavior: "smooth" });
    });
  }

  // Add scroll effect to header
  const header = document.querySelector('header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  // Add active class to current page nav link
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('nav a');
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentPage) {
      link.classList.add('active');
    }
  });

  // Setup card explorer dropdown (if on home page)
  if (document.getElementById('explorer-toggle')) {
    setupCardExplorer();
  }

  // Setup fade-up animations for overview section
  setupFadeUpAnimations();
});

// Fade-up animation on scroll
function setupFadeUpAnimations() {
  const fadeUpElements = document.querySelectorAll('.fade-up');

  if (fadeUpElements.length === 0) return;

  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);

  fadeUpElements.forEach(el => observer.observe(el));
}
