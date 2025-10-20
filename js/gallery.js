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
        loadingIndicator.style.display = 'none';

        // stats
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
                <span class="material-symbols-outlined">thumb_up</span>
            </button>
            <span class="upvote-count" data-card-id="${card.id}">${card.upvotes}</span>
            <button class="downvote-btn" data-card-id="${card.id}" aria-label="Downvote card">
                <span class="material-symbols-outlined">thumb_down</span>
            </button>
        </div>
    `;

    // Add upvote and downvote event listeners
    const upvoteBtn = cardDiv.querySelector('.upvote-btn');
    const downvoteBtn = cardDiv.querySelector('.downvote-btn');
    upvoteBtn.addEventListener('click', () => upvoteCard(card.id));
    downvoteBtn.addEventListener('click', () => downvoteCard(card.id));

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

// Downvote a card
async function downvoteCard(cardId) {
    const downvoteBtn = document.querySelector(`.downvote-btn[data-card-id="${cardId}"]`);
    const upvoteCount = document.querySelector(`.upvote-count[data-card-id="${cardId}"]`);

    // Prevent double-clicking
    if (downvoteBtn.classList.contains('downvoting')) return;

    downvoteBtn.classList.add('downvoting');
    downvoteBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/api/gallery/${cardId}/downvote`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`Failed to downvote: ${response.status}`);
        }

        const data = await response.json();

        // Update upvote count
        upvoteCount.textContent = data.new_upvote_count;

        // Add visual feedback
        downvoteBtn.classList.add('downvoted');
        upvoteCount.classList.add('pulse');

        setTimeout(() => {
            upvoteCount.classList.remove('pulse');
        }, 300);

    } catch (error) {
        console.error('Error downvoting card:', error);
        // Could show a toast notification here
    } finally {
        downvoteBtn.classList.remove('downvoting');
        downvoteBtn.disabled = false;
    }
}

// Change sort order
function changeSortOrder(sortBy) {
    if (currentSort === sortBy) return;

    currentSort = sortBy;
    currentPage = 1;

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

    const sortSelect = document.getElementById('sort-select');
    const loadMoreBtn = document.getElementById('load-more-btn');

    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            changeSortOrder(e.target.value);
        });
    }

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreCards);
    }
});
