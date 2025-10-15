from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import torch
import io
import base64
from PIL import Image
from models import Generator, nz
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
