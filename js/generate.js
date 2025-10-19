let currentCardImageData = null; // Store current card's base64 data for sharing

async function generateCard() {
    const button = document.getElementById('generate-btn');
    const cardContainer = document.getElementById('generated-card');
    const loadingIndicator = document.getElementById('loading');
    const shareButton = document.getElementById('share-to-gallery-btn');
    const shareConfirmation = document.getElementById('share-confirmation');

    button.disabled = true;
    button.textContent = 'Generating...';
    loadingIndicator.style.display = 'block';
    loadingIndicator.classList.add('visible');
    cardContainer.innerHTML = '';

    // Hide share button and confirmation when generating new card
    shareButton.style.display = 'none';
    shareConfirmation.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/api/card/generate`);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'failed') {
            throw new Error(data.error || 'Generation failed');
        }

        // Store the base64 image data (without the data:image/png;base64, prefix)
        currentCardImageData = data.image.replace('data:image/png;base64,', '');

        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card', 'flip');
        cardDiv.setAttribute('data-rarity', data.rarity.toLowerCase());

        // No favorite icon on generate page - that's only for gallery
        cardDiv.innerHTML = `
            <div class="card-inner">
                <div class="card-front">
                    <img src="assets/images/card-back.png" alt="Card Back">
                </div>
                <div class="card-back">
                    <img src="${data.image}" alt="AI Generated Card">
                    <div class="rarity-label">${data.rarity}</div>
                </div>
            </div>
        `;

        cardContainer.appendChild(cardDiv);
        attachCardEventListeners();

        // Show the "Share to Gallery" button after successful generation
        shareButton.style.display = 'block';

    } catch (error) {
        console.error('Error generating card:', error);
        cardContainer.innerHTML = `
            <div style="padding: var(--space-12); text-align: center; color: #ff6b6b;">
                <h3>Failed to generate card</h3>
                <p>${error.message}</p>
                <p style="font-size: 0.9em; margin-top: 10px;">
                    Make sure the backend server is running at ${API_URL}
                </p>
            </div>
        `;
        currentCardImageData = null;
    } finally {
        button.disabled = false;
        button.textContent = 'Generate New Card';
        loadingIndicator.style.display = 'none';
        loadingIndicator.classList.remove('visible');
    }
}

async function shareToGallery() {
    if (!currentCardImageData) {
        console.error('No card to share');
        return;
    }

    const shareButton = document.getElementById('share-to-gallery-btn');
    const shareConfirmation = document.getElementById('share-confirmation');

    // Disable button while sharing
    shareButton.disabled = true;
    shareButton.textContent = 'Sharing...';

    try {
        const response = await fetch(`${API_URL}/api/gallery/share`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_data: currentCardImageData
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to share: ${response.status}`);
        }

        const data = await response.json();
        console.log('Card shared successfully:', data);

        // Hide share button and show confirmation
        shareButton.style.display = 'none';
        shareConfirmation.style.display = 'block';

    } catch (error) {
        console.error('Error sharing card:', error);
        alert('Failed to share card to gallery. Please try again.');

        // Re-enable button on error
        shareButton.disabled = false;
        shareButton.textContent = 'Share to Gallery';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const shareBtn = document.getElementById('share-to-gallery-btn');

    if (generateBtn) {
        generateBtn.addEventListener('click', generateCard);
        generateCard(); // Generate first card automatically
    }

    if (shareBtn) {
        shareBtn.addEventListener('click', shareToGallery);
    }
});
