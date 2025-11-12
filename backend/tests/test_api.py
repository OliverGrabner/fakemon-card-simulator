import base64
from io import BytesIO
from PIL import Image


# ============================================================================
# Root / Health Check Endpoint
# ============================================================================

def test_root_endpoint_returns_200(client):
    """Test that the root endpoint returns 200 status code."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_endpoint_returns_correct_data(client):
    """Test that root endpoint returns expected JSON response."""
    response = client.get("/")
    data = response.json()
    assert data == {"status": "online"}


# ============================================================================
# Card Generation Endpoint
# ============================================================================

def test_generate_card_returns_200(client):
    """Test that the generate card endpoint returns 200 status code."""
    response = client.get("/api/card/generate")
    assert response.status_code == 200


def test_generate_card_has_correct_structure(client):
    """Test that generate endpoint returns correct data structure."""
    response = client.get("/api/card/generate")
    data = response.json()

    # Check response has required fields
    assert "image" in data
    assert "rarity" in data


def test_generate_card_image_is_base64(client):
    """Test that generated image is properly base64 encoded."""
    response = client.get("/api/card/generate")
    data = response.json()

    # Check image format
    assert data["image"].startswith("data:image/png;base64,")

    # Extract and validate base64 data
    base64_data = data["image"].split(",")[1]
    try:
        # This will raise if it's not valid base64
        decoded = base64.b64decode(base64_data)
        assert len(decoded) > 0
    except Exception as e:
        assert False, f"Invalid base64 data: {e}"


def test_generate_card_image_is_valid_png(client):
    """Test that generated image is a valid PNG file."""
    response = client.get("/api/card/generate")
    data = response.json()

    # Extract base64 data and decode
    base64_data = data["image"].split(",")[1]
    image_bytes = base64.b64decode(base64_data)

    # Try to open as PIL Image
    try:
        img = Image.open(BytesIO(image_bytes))
        assert img.format == "PNG"
    except Exception as e:
        assert False, f"Invalid PNG image: {e}"


def test_generate_card_rarity_is_valid(client):
    """Test that rarity is one of the expected values."""
    response = client.get("/api/card/generate")
    data = response.json()

    valid_rarities = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
    assert data["rarity"] in valid_rarities


def test_generate_card_creates_unique_images(client):
    """Test that multiple generations produce different images."""
    response1 = client.get("/api/card/generate")
    response2 = client.get("/api/card/generate")

    data1 = response1.json()
    data2 = response2.json()

    # Images should be different (very unlikely to be identical with random noise)
    assert data1["image"] != data2["image"]


# ============================================================================
# Gallery - Get Cards
# ============================================================================

def test_gallery_returns_200(client):
    """Test that the gallery endpoint returns 200 status code."""
    response = client.get("/api/gallery")
    assert response.status_code == 200


def test_gallery_has_correct_structure(client):
    """Test that gallery endpoint returns correct structure."""
    response = client.get("/api/gallery")
    data = response.json()

    # Check response has required fields
    assert "cards" in data
    assert "total" in data
    assert "has_more" in data

    # Check types
    assert isinstance(data["cards"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["has_more"], bool)


def test_gallery_empty_initially(client):
    """Test that gallery starts empty."""
    response = client.get("/api/gallery")
    data = response.json()

    assert data["cards"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


def test_gallery_sort_by_popular(client):
    """Test that popular sort returns cards sorted by upvotes."""
    # Share three cards with different upvote counts
    client.post("/api/gallery/share", json={"image_data": "image1"})
    client.post("/api/gallery/share", json={"image_data": "image2"})
    client.post("/api/gallery/share", json={"image_data": "image3"})

    # Upvote cards different amounts
    client.post("/api/gallery/1/upvote")
    client.post("/api/gallery/1/upvote")
    client.post("/api/gallery/1/upvote")  # Card 1: 3 upvotes

    client.post("/api/gallery/2/upvote")  # Card 2: 1 upvote

    # Card 3: 0 upvotes

    # Get gallery sorted by popular
    response = client.get("/api/gallery?sort_by=popular")
    data = response.json()

    # Should be ordered by upvotes: Card 1 (3), Card 2 (1), Card 3 (0)
    assert len(data["cards"]) == 3
    assert data["cards"][0]["upvotes"] == 3
    assert data["cards"][1]["upvotes"] == 1
    assert data["cards"][2]["upvotes"] == 0


def test_gallery_sort_by_recent(client):
    """Test that recent sort returns cards by creation date."""
    # Share three cards (most recent last)
    response1 = client.post("/api/gallery/share", json={"image_data": "image1"})
    response2 = client.post("/api/gallery/share", json={"image_data": "image2"})
    response3 = client.post("/api/gallery/share", json={"image_data": "image3"})

    # Get gallery sorted by recent
    response = client.get("/api/gallery?sort_by=recent")
    data = response.json()

    # Should be ordered by creation time (newest first)
    assert len(data["cards"]) == 3
    # Most recent should be first
    assert data["cards"][0]["id"] == 3
    assert data["cards"][1]["id"] == 2
    assert data["cards"][2]["id"] == 1


def test_gallery_invalid_sort_returns_400(client):
    """Test that invalid sort parameter returns 400 error."""
    response = client.get("/api/gallery?sort_by=invalid")
    assert response.status_code == 400


def test_gallery_pagination(client):
    """Test that pagination works correctly."""
    # Create 15 cards
    for i in range(15):
        client.post("/api/gallery/share", json={"image_data": f"image{i}"})

    # Get first page (limit 10)
    response = client.get("/api/gallery?page=1&limit=10")
    data = response.json()

    assert len(data["cards"]) == 10
    assert data["total"] == 15
    assert data["has_more"] is True

    # Get second page
    response = client.get("/api/gallery?page=2&limit=10")
    data = response.json()

    assert len(data["cards"]) == 5
    assert data["total"] == 15
    assert data["has_more"] is False


def test_gallery_limit_capped_at_100(client):
    """Test that limit is capped at 100 cards per page."""
    # Try to request 200 cards
    response = client.get("/api/gallery?limit=200")
    # Should not error, just cap at 100
    assert response.status_code == 200


# ============================================================================
# Gallery - Share Card
# ============================================================================

def test_share_card_returns_200(client):
    """Test that sharing a card returns 200 status code."""
    response = client.post("/api/gallery/share", json={"image_data": "test_image"})
    assert response.status_code == 200


def test_share_card_returns_correct_structure(client):
    """Test that share endpoint returns correct response structure."""
    response = client.post("/api/gallery/share", json={"image_data": "test_image"})
    data = response.json()

    assert "id" in data
    assert "image" in data
    assert "upvotes" in data
    assert "created_at" in data
    assert "message" in data


def test_share_card_starts_with_zero_upvotes(client):
    """Test that newly shared cards start with 0 upvotes."""
    response = client.post("/api/gallery/share", json={"image_data": "test_image"})
    data = response.json()

    assert data["upvotes"] == 0


def test_share_card_appears_in_gallery(client):
    """Test that shared card appears in gallery."""
    # Share a card
    share_response = client.post("/api/gallery/share", json={"image_data": "my_test_card"})
    card_id = share_response.json()["id"]

    # Get gallery
    gallery_response = client.get("/api/gallery")
    gallery_data = gallery_response.json()

    # Card should be in gallery
    assert len(gallery_data["cards"]) == 1
    assert gallery_data["cards"][0]["id"] == card_id


# ============================================================================
# Gallery - Voting
# ============================================================================

def test_upvote_card_returns_200(client):
    """Test that upvoting a card returns 200 status code."""
    # Create a card first
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Upvote it
    upvote_response = client.post(f"/api/gallery/{card_id}/upvote")
    assert upvote_response.status_code == 200


def test_upvote_card_increments_count(client):
    """Test that upvoting increases upvote count."""
    # Create a card
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Upvote it
    upvote_response = client.post(f"/api/gallery/{card_id}/upvote")
    upvote_data = upvote_response.json()

    assert upvote_data["success"] is True
    assert upvote_data["new_upvote_count"] == 1


def test_upvote_card_multiple_times(client):
    """Test that a card can be upvoted multiple times."""
    # Create a card
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Upvote 3 times
    for i in range(3):
        upvote_response = client.post(f"/api/gallery/{card_id}/upvote")
        data = upvote_response.json()
        assert data["new_upvote_count"] == i + 1


def test_downvote_card_returns_200(client):
    """Test that downvoting a card returns 200 status code."""
    # Create a card first
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Downvote it
    downvote_response = client.post(f"/api/gallery/{card_id}/downvote")
    assert downvote_response.status_code == 200


def test_downvote_card_decrements_count(client):
    """Test that downvoting decreases upvote count."""
    # Create a card
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Downvote it
    downvote_response = client.post(f"/api/gallery/{card_id}/downvote")
    downvote_data = downvote_response.json()

    assert downvote_data["success"] is True
    assert downvote_data["new_upvote_count"] == -1


def test_upvote_nonexistent_card_returns_404(client):
    """Test that upvoting a non-existent card returns 404."""
    response = client.post("/api/gallery/9999/upvote")
    assert response.status_code == 404


def test_downvote_nonexistent_card_returns_404(client):
    """Test that downvoting a non-existent card returns 404."""
    response = client.post("/api/gallery/9999/downvote")
    assert response.status_code == 404


def test_vote_card_can_go_negative(client):
    """Test that vote counts can go negative."""
    # Create a card
    response = client.post("/api/gallery/share", json={"image_data": "test"})
    card_id = response.json()["id"]

    # Downvote 5 times
    for _ in range(5):
        client.post(f"/api/gallery/{card_id}/downvote")

    # Get gallery to check count
    gallery_response = client.get("/api/gallery")
    cards = gallery_response.json()["cards"]

    assert cards[0]["upvotes"] == -5
