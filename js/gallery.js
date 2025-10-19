// Gallery state
let currentSort = 'popular';
let currentPage = 1;
let hasMoreCards = false;
let isLoading = false;

// Load gallery cards
async function loadGallery(append = false) {
    if (isLoading) return;

    const galleryGrid = document.getElementById('gallery-grid');
    const loadingIndicator = document.getElementById('gallery-loading');
    const emptyMessage = document.getElementById('gallery-empty');
    const loadMoreContainer = document.querySelector('.load-more-container');
    const statsDiv = document.getElementById('gallery-stats');
    const totalCardsCount = document.getElementById('total-cards-count');

    isLoading = true;

    // Show loading indicator
    loadingIndicator.style.display = 'block';

    // Clear grid if not appending
    if (!append) {
        galleryGrid.innerHTML = '';
        currentPage = 1;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/gallery?sort_by=${currentSort}&page=${currentPage}&limit=50`
        );

        if (!response.ok) {
            throw new Error(`Failed to load gallery: ${response.status}`);
        }

        const data = await response.json();

        // Hide loading indicator
        loadingIndicator.style.display = 'none';

        // Show stats
        if (data.total > 0) {
            totalCardsCount.textContent = data.total;
            statsDiv.style.display = 'block';
        }

        // Check if gallery is empty
        if (data.cards.length === 0 && currentPage === 1) {
            emptyMessage.style.display = 'block';
            loadMoreContainer.style.display = 'none';
            return;
        } else {
            emptyMessage.style.display = 'none';
        }

        // Display cards
        data.cards.forEach(card => {
            const cardElement = createGalleryCard(card);
            galleryGrid.appendChild(cardElement);
        });

        // Update pagination
        hasMoreCards = data.has_more;

        // Show/hide load more button
        if (hasMoreCards) {
            loadMoreContainer.style.display = 'block';
        } else {
            loadMoreContainer.style.display = 'none';
        }

    } catch (error) {
        console.error('Error loading gallery:', error);
        loadingIndicator.style.display = 'none';

        if (!append) {
            galleryGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ff6b6b;">
                    <h3>Failed to load gallery</h3>
                    <p>${error.message}</p>
                    <button class="btn" onclick="loadGallery()">Try Again</button>
                </div>
            `;
        }
    } finally {
        isLoading = false;
    }
}

// Create a gallery card element
function createGalleryCard(card) {
    const cardDiv = document.createElement('div');
    cardDiv.classList.add('gallery-card');
    cardDiv.setAttribute('data-card-id', card.id);

    cardDiv.innerHTML = `
        <div class="card-image-wrapper">
            <img src="${card.image}" alt="Generated Card" loading="lazy">
        </div>
        <div class="card-upvote-section">
            <button class="upvote-btn" data-card-id="${card.id}" aria-label="Upvote card">
                <span class="heart-icon">❤</span>
            </button>
            <span class="upvote-count" data-card-id="${card.id}">${card.upvotes}</span>
        </div>
    `;

    // Add upvote event listener
    const upvoteBtn = cardDiv.querySelector('.upvote-btn');
    upvoteBtn.addEventListener('click', () => upvoteCard(card.id));

    return cardDiv;
}

// Upvote a card
async function upvoteCard(cardId) {
    const upvoteBtn = document.querySelector(`.upvote-btn[data-card-id="${cardId}"]`);
    const upvoteCount = document.querySelector(`.upvote-count[data-card-id="${cardId}"]`);

    // Prevent double-clicking
    if (upvoteBtn.classList.contains('upvoting')) return;

    upvoteBtn.classList.add('upvoting');
    upvoteBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/gallery/${cardId}/upvote`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`Failed to upvote: ${response.status}`);
        }

        const data = await response.json();

        // Update upvote count
        upvoteCount.textContent = data.new_upvote_count;

        // Add visual feedback
        upvoteBtn.classList.add('upvoted');
        upvoteCount.classList.add('pulse');

        setTimeout(() => {
            upvoteCount.classList.remove('pulse');
        }, 300);

    } catch (error) {
        console.error('Error upvoting card:', error);
        // Could show a toast notification here
    } finally {
        upvoteBtn.classList.remove('upvoting');
        upvoteBtn.disabled = false;
    }
}

// Change sort order
function changeSortOrder(sortBy) {
    if (currentSort === sortBy) return;

    currentSort = sortBy;
    currentPage = 1;

    // Update button states
    document.getElementById('sort-popular').classList.toggle('active', sortBy === 'popular');
    document.getElementById('sort-recent').classList.toggle('active', sortBy === 'recent');

    // Reload gallery
    loadGallery(false);
}

// Load more cards
function loadMoreCards() {
    currentPage++;
    loadGallery(true);
}

// Initialize gallery on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load initial gallery
    loadGallery();

    // Add event listeners for sort buttons
    const sortPopularBtn = document.getElementById('sort-popular');
    const sortRecentBtn = document.getElementById('sort-recent');
    const loadMoreBtn = document.getElementById('load-more-btn');

    if (sortPopularBtn) {
        sortPopularBtn.addEventListener('click', () => changeSortOrder('popular'));
    }

    if (sortRecentBtn) {
        sortRecentBtn.addEventListener('click', () => changeSortOrder('recent'));
    }

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreCards);
    }
});
