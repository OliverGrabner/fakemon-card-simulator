from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from models import Generator, nz
from database import get_db, init_db, GeneratedCard
import torch
import random

import io
import base64
from PIL import Image
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    print("Backend ready")
    yield
    # TODO: possible cleanup needed 


app = FastAPI(lifespan=lifespan)
ALLOWED_ORIGINS = os.getenv("FRONTEND_URL", "http://localhost:5500,http://127.0.0.1:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # only allow api requests from vercel frontend 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

CKPT_PATH = Path("checkpoints/gan_checkpoint.pth")
netG = Generator(ngpu=1 if torch.cuda.is_available() else 0).to(device)

checkpoint = torch.load(CKPT_PATH, map_location=device)
netG.load_state_dict(checkpoint['generator_state_dict'])
netG.eval()
print("Generator loaded!")

# Weighted Rarity Selection:
# Common: 70%, Uncommon: 15%, Rare: 8%, Epic: 6%, Legendary: 1%
def get_random_rarity():
    rand = random.random() * 100
    if rand < 70: return 'Common'
    elif rand < 85: return 'Uncommon'
    elif rand < 93: return 'Rare'
    elif rand < 99: return 'Epic'
    else: return 'Legendary'

@app.get("/")
def root():
    return {"status": "online"}

@app.get("/api/card/generate")
def generate_card():
    # Generate random noise and run through generator
    with torch.no_grad():
        noise = torch.randn(1, nz, 1, 1, device=device)
        fake_image = netG(noise)

    # Denormalize from [-1, 1] to [0, 1]
    img_tensor = (fake_image[0] + 1) / 2
    img_tensor = img_tensor.clamp(0, 1)

    # Convert to PIL Image
    img_np = (img_tensor.permute(1, 2, 0).cpu().numpy() * 255).astype('uint8')
    img = Image.fromarray(img_np)

    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    return {
        "image": f"data:image/png;base64,{img_base64}",
        "rarity": get_random_rarity()
    }

@app.post("/api/gallery/share")
def share_card(request: dict, db: Session = Depends(get_db)):
    """Save a generated card to the public gallery"""
    
    card = GeneratedCard(
        image_data=request["image_data"],
        upvotes=0,
        created_at=datetime.now()
    )
    
    db.add(card)
    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "image": f"data:image/png;base64,{card.image_data}",
        "upvotes": card.upvotes,
        "created_at": card.created_at,
        "message": "Card shared to gallery successfully!"
    }


@app.get("/api/gallery")
def get_gallery(sort_by: str = "popular", page: int = 1, limit: int = 50, db: Session = Depends(get_db)):
    """Get paginated gallery of all shared cards"""
    if sort_by not in ["popular", "recent"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'popular' or 'recent'")

    if limit > 100:
        limit = 100

    query = db.query(GeneratedCard)

    if sort_by == "popular":
        query = query.order_by(desc(GeneratedCard.upvotes), desc(GeneratedCard.created_at))
    else:
        query = query.order_by(desc(GeneratedCard.created_at))

    total = query.count()
    offset = (page - 1) * limit
    cards = query.offset(offset).limit(limit).all()

    return {
        "cards": [
            {
                "id": card.id,
                "image": f"data:image/png;base64,{card.image_data}",
                "upvotes": card.upvotes,
                "created_at": card.created_at
            }
            for card in cards
        ],
        "total": total,
        "has_more": (page * limit) < total
    }


@app.post("/api/gallery/{card_id}/upvote")
def upvote_card(card_id: int, db: Session = Depends(get_db)):
    """Upvote a card in the gallery"""
    card = db.query(GeneratedCard).filter(GeneratedCard.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.upvotes += 1
    db.commit()

    return {
        "success": True,
        "new_upvote_count": card.upvotes,
        "message": "Upvote added successfully"
    }
