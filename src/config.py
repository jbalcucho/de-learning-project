from pathlib import Path

# Root
ROOT_DIR = Path(__file__).parent.parent

# Data files
DATA_DIR = ROOT_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

LINKS_RAW_DIR = RAW_DATA_DIR / "links.csv"
MOVIES_RAW_DIR = RAW_DATA_DIR / "movies.csv"
RATINGS_RAW_DIR = RAW_DATA_DIR / "ratings.csv"
TAGS_RAW_DIR = RAW_DATA_DIR / "tags.csv"

MOVIES_CLEANED_DIR = PROCESSED_DATA_DIR / "movies_cleaned.json"
MOVIE_ID_TITLE_YEAR_DIR = PROCESSED_DATA_DIR / "movie_id_title_year.csv"
UNIQUE_GENRES_DIR = PROCESSED_DATA_DIR / "unique_genres.txt"

# Code files
SRC_DIR = ROOT_DIR / "src"

# Test files
TESTS_DIR = ROOT_DIR / "tests"

# Report files
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
