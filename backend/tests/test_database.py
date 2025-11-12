from datetime import datetime, timedelta
from sqlalchemy import desc
from database import GeneratedCard, SessionLocal


def test_create_card_with_minimal_data(client):
    """Test creating a card with only required fields."""
    db = SessionLocal()
    try:
        card = GeneratedCard(image_data="fake_base64_image_data")
        db.add(card)
        db.commit()
        db.refresh(card)

        # Verify card was created
        assert card.id is not None
        assert card.image_data == "fake_base64_image_data"
        assert card.upvotes == 0  # Default value
        assert card.created_at is not None
    finally:
        db.close()


def test_create_card_with_all_fields(client):
    """Test creating a card with all fields specified."""
    db = SessionLocal()
    try:
        test_time = datetime.now()
        card = GeneratedCard(
            image_data="test_image_data",
            upvotes=42,
            created_at=test_time
        )
        db.add(card)
        db.commit()
        db.refresh(card)

        assert card.id is not None
        assert card.image_data == "test_image_data"
        assert card.upvotes == 42
        assert card.created_at == test_time
    finally:
        db.close()


def test_card_id_auto_increments(client):
    """Test that card IDs auto-increment."""
    db = SessionLocal()
    try:
        card1 = GeneratedCard(image_data="image1")
        card2 = GeneratedCard(image_data="image2")

        db.add(card1)
        db.add(card2)
        db.commit()
        db.refresh(card1)
        db.refresh(card2)

        assert card2.id > card1.id
    finally:
        db.close()


def test_update_card_upvotes(client):
    """Test updating a card's upvote count."""
    db = SessionLocal()
    try:
        card = GeneratedCard(image_data="test", upvotes=5)
        db.add(card)
        db.commit()
        db.refresh(card)

        # Update upvotes
        card.upvotes = 10
        db.commit()

        # Fetch again and verify
        fetched = db.query(GeneratedCard).filter(GeneratedCard.id == card.id).first()
        assert fetched.upvotes == 10
    finally:
        db.close()


def test_query_cards_by_upvotes(client):
    """Test querying cards sorted by upvotes."""
    db = SessionLocal()
    try:
        # Create cards with different upvote counts
        card1 = GeneratedCard(image_data="image1", upvotes=5)
        card2 = GeneratedCard(image_data="image2", upvotes=20)
        card3 = GeneratedCard(image_data="image3", upvotes=10)

        db.add_all([card1, card2, card3])
        db.commit()

        # Query sorted by upvotes descending
        cards = db.query(GeneratedCard).order_by(desc(GeneratedCard.upvotes)).all()

        assert cards[0].upvotes == 20
        assert cards[1].upvotes == 10
        assert cards[2].upvotes == 5
    finally:
        db.close()


def test_query_cards_by_created_at(client):
    """Test querying cards sorted by creation time."""
    db = SessionLocal()
    try:
        now = datetime.now()
        card1 = GeneratedCard(image_data="image1", created_at=now - timedelta(hours=2))
        card2 = GeneratedCard(image_data="image2", created_at=now)
        card3 = GeneratedCard(image_data="image3", created_at=now - timedelta(hours=1))

        db.add_all([card1, card2, card3])
        db.commit()

        # Query sorted by created_at descending (most recent first)
        cards = db.query(GeneratedCard).order_by(desc(GeneratedCard.created_at)).all()

        assert cards[0].image_data == "image2"
        assert cards[1].image_data == "image3"
        assert cards[2].image_data == "image1"
    finally:
        db.close()


def test_delete_card(client):
    """Test deleting a card from the database."""
    db = SessionLocal()
    try:
        card = GeneratedCard(image_data="to_delete")
        db.add(card)
        db.commit()
        card_id = card.id

        # Delete the card
        db.delete(card)
        db.commit()

        # Verify it's gone
        fetched = db.query(GeneratedCard).filter(GeneratedCard.id == card_id).first()
        assert fetched is None
    finally:
        db.close()


def test_card_count(client):
    """Test counting total cards in database."""
    db = SessionLocal()
    try:
        # Start with empty database
        initial_count = db.query(GeneratedCard).count()

        # Add 3 cards
        for i in range(3):
            card = GeneratedCard(image_data=f"image{i}")
            db.add(card)
        db.commit()

        # Verify count increased by 3
        final_count = db.query(GeneratedCard).count()
        assert final_count == initial_count + 3
    finally:
        db.close()


def test_pagination(client):
    """Test paginating through cards."""
    db = SessionLocal()
    try:
        # Create 10 cards
        for i in range(10):
            card = GeneratedCard(image_data=f"image{i}")
            db.add(card)
        db.commit()

        # Page 1: Get first 5
        page1 = db.query(GeneratedCard).offset(0).limit(5).all()
        assert len(page1) == 5

        # Page 2: Get next 5
        page2 = db.query(GeneratedCard).offset(5).limit(5).all()
        assert len(page2) == 5

        # No overlap between pages
        page1_ids = {card.id for card in page1}
        page2_ids = {card.id for card in page2}
        assert page1_ids.isdisjoint(page2_ids)
    finally:
        db.close()
