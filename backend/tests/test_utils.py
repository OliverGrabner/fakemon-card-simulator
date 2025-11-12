import random
from app import get_random_rarity


def test_returns_string():
    """Test that get_random_rarity returns a string."""
    result = get_random_rarity()
    assert isinstance(result, str)


def test_returns_valid_rarity():
    """Test that the function only returns valid rarity values."""
    valid_rarities = {'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'}

    for _ in range(100):
        result = get_random_rarity()
        assert result in valid_rarities


def test_all_rarities_can_occur():
    """Test that all rarities can theoretically occur (no dead code)."""
    random.seed(42)
    rarities_found = set()

    # Run enough iterations to find all rarities 
    for _ in range(10000):
        rarities_found.add(get_random_rarity())

    # All 5 rarities should appear at least once
    expected_rarities = {'Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'}
    assert rarities_found == expected_rarities


def test_distribution_is_weighted_correctly():
    """Test that distribution matches expected probabilities.

    Expected distribution:
    - Common: 70%
    - Uncommon: 15%
    - Rare: 8%
    - Epic: 6%
    - Legendary: 1%
    """
    counts = {
        'Common': 0,
        'Uncommon': 0,
        'Rare': 0,
        'Epic': 0,
        'Legendary': 0
    }

    num_samples = 20000
    for _ in range(num_samples):
        rarity = get_random_rarity()
        counts[rarity] += 1

    # Calculate percentages
    percentages = {k: v / num_samples for k, v in counts.items()}

    # Allow 5% margin of error for each category
    assert 0.65 < percentages['Common'] < 0.75, f"Common: {percentages['Common']:.2%}"
    assert 0.12 < percentages['Uncommon'] < 0.18, f"Uncommon: {percentages['Uncommon']:.2%}"
    assert 0.06 < percentages['Rare'] < 0.10, f"Rare: {percentages['Rare']:.2%}"
    assert 0.04 < percentages['Epic'] < 0.08, f"Epic: {percentages['Epic']:.2%}"
    assert 0.005 < percentages['Legendary'] < 0.02, f"Legendary: {percentages['Legendary']:.2%}"


def test_deterministic_with_seed():
    """Test that results are reproducible with random seed."""
    random.seed(123)
    results1 = [get_random_rarity() for _ in range(10)]

    random.seed(123)
    results2 = [get_random_rarity() for _ in range(10)]

    assert results1 == results2, "Results should be identical with same seed"
