# tests/test_ingestion.py
import pytest
from src.ingestion import (
    load_movie_data,
    get_unique_genres,
    transform_movie_records
)

# Test data simulating the raw CSV content
@pytest.fixture
def sample_raw_movies():
    """Provides a sample list of dictionaries, as loaded from CSV."""
    return [
        {'movieId': '1', 'title': 'Toy Story (1995)', 'genres': 'Adventure|Animation|Children'},
        {'movieId': '2', 'title': 'Jumanji (1995)', 'genres': 'Adventure|Fantasy'},
        {'movieId': '3', 'title': 'Grumpier Old Men (1995)', 'genres': '(no genres listed)'},
        {'movieId': '4', 'title': 'Heat (1995)', 'genres': 'Action|Crime|Thriller'},
    ]

def test_get_unique_genres(sample_raw_movies):
    """
    Tests that unique genres are extracted correctly, and the placeholder is ignored.
    """
    # Act
    result = get_unique_genres(sample_raw_movies)
    
    # Assert
    expected_genres = {'Adventure', 'Animation', 'Children', 'Fantasy', 'Action', 'Crime', 'Thriller'}
    assert result == expected_genres
    assert '(no genres listed)' not in result

def test_transform_movie_records(sample_raw_movies):
    """
    Tests the main transformation logic: type casting and feature extraction.
    """
    # Act
    result = transform_movie_records(sample_raw_movies)

    # Assert
    # Check the first record
    toy_story = result[0]
    assert toy_story['movieId'] == 1  # Should be an integer
    assert toy_story['title'] == 'Toy Story' # Year should be removed
    assert toy_story['year'] == 1995 # Year should be extracted as an integer
    assert toy_story['genres'] == ['Adventure', 'Animation', 'Children'] # Should be a list

    # Check the third record
    grumpier = result[2]
    assert grumpier['movieId'] == 3
    assert grumpier['title'] == 'Grumpier Old Men'
    assert grumpier['year'] == 1995
    assert grumpier['genres'] == ['(no genres listed)']

def test_load_movie_data_error_handling():
    """
    Tests that the loader returns an empty list for a non-existent file.
    """
    # Act
    result = load_movie_data("non_existent_file.csv")

    # Assert
    assert result == []