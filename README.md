# 🃏 Fakémon Card Simulator 
     🟥🟥🟥
  🟥🟥🟥🟥🟥
  ⬛⬛⬜⬛⬛
  ⬜⬜⬜⬜⬜
     ⬜⬜⬜

A full-stack web app that lets you open AI-generated Pokémon card packs and generate brand new cards in real-time using a GAN model I trained on my laptop.

A full-stack web application that generates AI-powered Pokémon cards in real-time using a custom-trained DCGAN model. Features interactive card pack opening, real-time generation via REST API, and a complete deployment pipeline across multiple cloud platforms.

**Live Demo:** [https://fakemon-card-simulator.vercel.app](https://fakemon-card-simulator.vercel.app)

**Model Training Repo:** [DCGAN-Pokemon-Card-Generator](https://github.com/OliverGrabner/DCGAN-Pokemon-Card-Generator)

## Project Overview

This project demonstrates end-to-end machine learning deployment, from training a generative model to building a production-ready web application. I trained a DCGAN on 11,044 Pokémon TCG cards and built a full-stack application to serve the model predictions in real-time.

### Key Features
- **Real-time AI generation** - REST API endpoint generates unique cards on demand using PyTorch inference
- **Interactive pack opening** - Client-side JavaScript generates random 10-card packs with weighted rarity distribution
- **Persistent favorites system** - localStorage-based state management for saved cards
- **3D animations** - CSS transforms with mouse-tracking tilt effects and flip animations
- **Dual-platform deployment** - Split architecture optimized for serverless constraints

## Technical Architecture

### System Design

The application uses a **microservices architecture** with separated frontend and backend deployments:

```
┌─────────────────┐
│  Vercel (CDN)   │  ← Static HTML/CSS/JS
│    Frontend     │
└────────┬────────┘
         │ HTTPS/REST
         ▼
┌─────────────────┐
│  Render Cloud   │  ← FastAPI + PyTorch
│    Backend      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DCGAN Generator │  ← 120MB checkpoint
│  (PyTorch CNN)  │
└─────────────────┘
```

**Why this architecture?**
I originally tried deploying everything to Vercel, but ran into their 250MB serverless function limit. PyTorch alone is ~700MB, plus the 120MB model checkpoint. This forced me to learn how to architect a split deployment where the frontend and backend are hosted separately and communicate via REST API.

### Frontend (Vercel)

**Tech Stack:** Vanilla JavaScript, HTML5, CSS3

**Key Implementation Details:**
- **No framework dependencies** - Built with vanilla JS to minimize bundle size and demonstrate DOM manipulation skills
- **3D CSS transforms** - Implemented mouse-position-based card tilt using `rotateX()` and `rotateY()` with calculated percentages from cursor position
- **Intersection Observer API** - Lazy-loading animations trigger when elements enter viewport
- **localStorage state management** - Persistent favorites system without backend database
- **Fetch API integration** - Async/await patterns for backend communication with error handling

**Component Breakdown:**
- `js/main.js` (328 lines) - Card rendering, animations, favorites logic, weighted rarity algorithm
- `js/generate.js` (73 lines) - API integration, base64 image handling, loading states

### Backend (Render)

**Tech Stack:** Python 3.11, FastAPI, PyTorch, Docker

**Key Implementation Details:**
- **FastAPI REST API** - Asynchronous endpoint serving PyTorch model inference
- **Model optimization** - Generator loaded once on startup (not per-request) to reduce latency
- **Base64 encoding** - Converts PyTorch tensors → PIL Images → base64 strings to avoid file storage
- **CORS configuration** - Environment-based origin whitelisting for cross-domain requests
- **Docker containerization** - Multi-stage build to manage 700MB+ dependency tree

**API Endpoints:**
- `GET /` - Health check endpoint (returns `{"status": "online"}`)
- `GET /api/card/generate` - Generates card from random latent vector (returns base64 image + rarity)

**Inference Pipeline:**
1. Generate 100D random noise vector
2. Pass through DCGAN Generator (5 transposed conv layers)
3. Denormalize tensor from [-1, 1] to [0, 255]
4. Convert to PIL Image → base64 string
5. Assign weighted random rarity (70% Common → 1% Legendary)
6. Return JSON response

### Machine Learning Model

**Architecture:** DCGAN (Deep Convolutional GAN)

**Training Details:**
- **Dataset:** 11,044 Pokémon TCG cards (filtered to standard rectangular designs)
- **Hardware:** NVIDIA RTX 3050 (4GB VRAM)
- **Duration:** 13 hours
- **Output Resolution:** 96x64 pixels (memory-constrained)

**Network Architecture:**
- **Generator:** 5 transposed convolutional layers with BatchNorm and ReLU
  - Input: 100D latent vector
  - Output: 3-channel RGB image (96x64)
- **Discriminator:** 5 convolutional layers with LeakyReLU (training only)
  - Binary classification: real vs. generated

**Key Learning:** Had to downsample from 600x825 to 96x64 due to GPU memory constraints. Learned to balance model capacity with available hardware.

## Deployment & DevOps

### Challenge: Platform Size Limits

**Problem:** Initially attempted to deploy entire stack to Vercel as serverless functions.

**Blocker:** Vercel has a 250MB uncompressed limit for serverless functions. My backend requirements:
- PyTorch: ~700MB
- Model checkpoint: ~120MB
- Dependencies (FastAPI, Pillow, etc.): ~50-100MB
- **Total: ~870-920MB** (3.5x over limit)

**Solution:** Architected split deployment across two platforms:

1. **Frontend → Vercel**
   - Optimized for static asset delivery
   - Global CDN distribution
   - Automatic HTTPS
   - GitHub integration for CI/CD

2. **Backend → Render**
   - Supports Docker containers (no size limit)
   - 512MB RAM on free tier (sufficient for inference)
   - Persistent Python process (not serverless)
   - Auto-deploy on git push

### Configuration Files

**Docker Setup (`backend/Dockerfile`):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc g++
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Vercel Config (`vercel.json`):**
```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

**Render Config (`render.yaml`):**
```yaml
services:
  - type: web
    name: fakemon-backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    plan: free
```

### CORS Configuration

Since frontend and backend are on different domains, had to implement CORS:

```python
# backend/app.py
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL", "http://localhost:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Environment variable `FRONTEND_URL` set in Render dashboard to Vercel domain.

## Technical Skills Demonstrated

### Machine Learning & AI
- Trained DCGAN from scratch using PyTorch
- Implemented Generator and Discriminator networks
- Understood adversarial training dynamics
- Managed GPU memory constraints
- Converted research paper architecture to production code

### Backend Development
- Built RESTful API with FastAPI
- Implemented async endpoints for concurrent requests
- Managed PyTorch model lifecycle (load once, inference many)
- Handled tensor-to-image conversion pipeline
- Configured CORS for cross-origin requests
- Optimized for cold start performance on free tier

### Frontend Development
- Vanilla JavaScript (DOM manipulation, event handling)
- Async/await patterns for API consumption
- CSS 3D transforms and animations
- Intersection Observer API for performance
- localStorage for client-side persistence
- Responsive design principles

### DevOps & Deployment
- Dockerized Python application with multi-stage builds
- Configured environment-based deployments
- Set up CI/CD pipelines with GitHub integration
- Debugged platform-specific constraints (size limits, cold starts)
- Managed secrets and environment variables across platforms
- Optimized build times and dependency caching

### Problem-Solving
- **Platform constraints** - Learned to split architecture when monolithic deployment failed
- **Memory optimization** - Reduced model resolution to fit GPU constraints
- **Network efficiency** - Used base64 encoding to avoid S3/storage costs
- **Performance tuning** - Implemented model preloading to reduce inference latency
- **Cross-origin communication** - Debugged and configured CORS policies

## Running Locally

### Frontend Only
```bash
git clone https://github.com/OliverGrabner/fakemon-card-simulator.git
cd fakemon-card-simulator
python -m http.server 8000
```
Visit `http://localhost:8000` - Pack opening works, but live generation requires backend.

### Full Stack

**Backend:**
```bash
cd backend
pip install -r requirements.txt
# Ensure model checkpoint exists at backend/checkpoints/gan_checkpoint.pth
uvicorn app:app --reload
```

**Frontend:**
Update `js/generate.js` line 1:
```javascript
const API_URL = 'http://localhost:8000';
```

Then open `index.html` in browser.

## Performance Characteristics

**Frontend (Vercel CDN):**
- Load time: 1-2 seconds (globally cached)
- Pack opening: Instant (client-side only)
- Animations: 60fps on modern browsers

**Backend (Render Free Tier):**
- Cold start: 30-60 seconds (after 15min inactivity)
- Warm inference: 5-10 seconds per card
- Concurrent requests: Limited by 512MB RAM

## Challenges & Solutions

### 1. Deployment Size Limits
**Problem:** PyTorch + model = 820MB, Vercel limit = 250MB
**Solution:** Split deployment across Vercel (frontend) + Render (backend)
**Learning:** Microservices architecture, platform selection based on constraints

### 2. GPU Memory During Training
**Problem:** 4GB VRAM insufficient for full-resolution cards
**Solution:** Downsampled to 96x64, reduced batch size
**Learning:** Hardware-constrained optimization, resolution vs. quality tradeoffs

### 3. Cold Start Latency
**Problem:** Free tier spins down, 60s first request
**Solution:** Preload model on startup, not per-request
**Learning:** Application lifecycle management, startup optimization

### 4. CORS Errors in Production
**Problem:** Browser blocked cross-origin API calls
**Solution:** Configured FastAPI CORS middleware with environment-based origins
**Learning:** Web security policies, environment variable management

### 5. Base64 Image Transfer
**Problem:** Needed image delivery without S3/storage costs
**Solution:** Encode images as base64 strings in JSON response
**Learning:** Data encoding techniques, cost optimization

## Future Enhancements

**Technical Improvements:**
- Implement Redis caching layer to reduce inference calls
- Add PostgreSQL database for persistent favorites across devices
- Upgrade to Conditional GAN to allow type/attribute specification
- Retrain at higher resolution with cloud GPU (AWS EC2 p3 instance)
- Add WebSocket support for real-time generation progress

**Feature Additions:**
- User authentication and cloud-synced collections
- Social sharing with Open Graph meta tags
- Download generated cards as PNG
- Card rarity statistics dashboard
- Batch generation endpoint

## Tech Stack Summary

| Category | Technology |
|----------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **ML Framework** | PyTorch 2.x |
| **Model** | DCGAN (5-layer Generator/Discriminator) |
| **Image Processing** | Pillow (PIL) |
| **Containerization** | Docker |
| **Frontend Host** | Vercel (Edge Network) |
| **Backend Host** | Render (Docker Container) |
| **CI/CD** | GitHub Integration (auto-deploy) |
| **APIs** | REST (JSON), Fetch API, localStorage |

## Credits

- **Dataset:** [Pokemon TCG Dataset](https://github.com/PokemonTCG/pokemon-tcg-data) (11,044 cards)
- **Architecture:** Based on [DCGAN paper](https://arxiv.org/abs/1511.06434) (Radford et al., 2015)
- **Disclaimer:** Not affiliated with Nintendo or The Pokémon Company. Educational project only.

## License

MIT License - Educational and portfolio purposes. Pokémon and related trademarks are property of Nintendo/The Pokémon Company.
