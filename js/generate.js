async function generateCard() {
    const button = document.getElementById('generate-btn');
    const cardContainer = document.getElementById('generated-card');
    const loadingIndicator = document.getElementById('loading');

    button.disabled = true;
    button.textContent = 'Generating...';
    loadingIndicator.style.display = 'block';
    loadingIndicator.classList.add('visible');
    cardContainer.innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/api/card/generate`);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === 'failed') {
            throw new Error(data.error || 'Generation failed');
        }

        const cardDiv = document.createElement('div');
        cardDiv.classList.add('card', 'flip');
        cardDiv.setAttribute('data-rarity', data.rarity.toLowerCase());

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
            <div class="favorite-icon" title="Favorite this card">&#10084;</div>
        `;

        cardContainer.appendChild(cardDiv);
        attachCardEventListeners();

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
    } finally {
        button.disabled = false;
        button.textContent = 'Generate New Card';
        loadingIndicator.style.display = 'none';
        loadingIndicator.classList.remove('visible');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateCard);
        generateCard(); // Generate first card automatically
    }
});
