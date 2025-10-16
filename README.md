#  Fakémon Card Simulator 🟥⬛⬜

![Fakemon Simulator Screenshot](/assets/images/fakemon-simulator.png)

A full-stack web app that lets you open AI-generated Pokémon card packs and generate brand new cards in real-time using a unique architecture DCGAN model I trained on my laptop. Real time generation is supported via REST API, and complete deployment pipeline across Vercel & Render 

**Live Demo:** [https://fakemon-card-simulator.vercel.app](https://fakemon-card-simulator.vercel.app)

**Model Training Repo:** [DCGAN-Pokemon-Card-Generator](https://github.com/OliverGrabner/DCGAN-Pokemon-Card-Generator)

## What This Does

I built this because I was really interested in GANs (Generative Adversarial Networks) and wanted to combine that with something fun. The result is a full-stack application where you can:

- **Open card packs** - Get 10 random cards from a pool of pre-generated images
- **Generate new cards** - Create completely unique cards in real-time using the trained GAN model
- **Save favorites** - Click the heart icon to save cards you like (stored in your browser)
- **Explore cards** - Browse through all the cached generated cards on the home page

The cards aren't super crisp because I trained the model on my laptop (NVIDIA RTX 3050 with 4GB VRAM) for about 13 hours, but I think they turned out pretty cool!

## Key Features
- **Real-time AI generation** - REST API endpoint generates unique cards on demand using PyTorch inference
- **Interactive pack opening** - Client-side JavaScript generates random 10-card packs with weighted rarity distribution
- **Persistent favorites system** - localStorage-based state management for saved cards
- **3D animations** - CSS transforms with mouse-tracking tilt effects and flip animations
- **Dual-platform deployment** - Split architecture optimized for serverless constraints

## Technical Architecture

**Frontend (Vercel):**
- Vanilla JavaScript (no frameworks - wanted to keep it simple)
- CSS3 with 3D transforms for the card flip animations
- Hosted on Vercel for free

**Backend (Render):**
- FastAPI server running PyTorch for model inference
- Takes random noise, runs it through the Generator network, and returns a base64 image
- Dockerized and deployed on Render's free tier
- Also assigns a random rarity (Common, Uncommon, Rare, Epic, Legendary)

When you click "Generate Card" on the website, your browser sends a request to the backend, which generates a completely new card on the spot and sends it back.


**Why this architecture?**
I originally tried deploying everything to Vercel, but ran into their 250MB serverless function limit. PyTorch alone is ~700MB, plus the 120MB model checkpoint. This forced me to learn how to architect a split deployment where the frontend and backend are hosted separately and communicate via REST API.

## Tech Stack


- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python, FastAPI, PyTorch, Uvicorn
- **ML Model:** DCGAN trained with PyTorch
- **Deployment:** Vercel (frontend) + Render (backend)
- **Image Processing:** Pillow/PIL
- **Containerization:** Docker

**API Endpoints:**
- `GET /` - Health check endpoint (returns `{"status": "online"}`)
- `GET /api/card/generate` - Generates card from random latent vector (returns base64 image + rarity)

## Challenges I Ran Into

**Memory constraints:** My laptop only has 4GB VRAM, so I had to train at a lower resolution (96x64) instead of full card size. That's why the images are a bit blurry.

**Deployment size limits:** PyTorch is very large (~700MB). Vercel has a 250MB limit for serverless functions, so I had to split the deployment - frontend on Vercel, backend on Render.

**Cold starts:** Render's free tier spins down after 15 minutes. The first card generation after that can take 30-60 seconds while the server wakes up and loads the model.

**3D card animations:** Getting the card flip and tilt effects to feel smooth took a lot of tweaking. I used CSS transforms and had to carefully handle the mouse position calculations.

## Future Improvements

Some things I'd like to add if I come back to this:
- Train at higher resolution (need a better GPU)
- Let users download their generated cards
- Add social sharing features
- Maybe experiment with conditional GANs so you could specify card attributes 

## Credits

- Training dataset: [Pokemon TCG Dataset](https://github.com/PokemonTCG/pokemon-tcg-data) (11,044 cards)
- DCGAN architecture based on the original [DCGAN paper](https://arxiv.org/abs/1511.06434)

## License

This is a project for educational perposes only. The Pokémon name and TCG card designs are trademarks of Nintendo/The Pokémon Company. I do not own any of the designs trained on. (Lawsuit Avoided)

## Tech Stack 

| Category | Technology |
|----------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **ML Framework** | PyTorch  |
| **Model** | DCGAN (5-layer Generator/Discriminator) |
| **Image Processing** | Pillow (PIL) |
| **Containerization** | Docker |
| **Frontend Host** | Vercel (Edge Network) |
| **Backend Host** | Render (Docker Container) |
| **CI/CD** | GitHub Integration (auto-deploy) |
| **APIs** | REST (JSON), Fetch API, localStorage |
