# src/ingestion.py
import re
import os
import csv
import json
import config
from pathlib import Path

# --- LOADING AND VALIDATION FUNCTIONS ---


def load_movie_data(file_path: Path) -> list:
    """
    Loads movie data from a CSV, handling file errors and validating headers.
    """
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_columns = {"movieId", "title", "genres"}
            if not required_columns.issubset(reader.fieldnames):
                raise ValueError(
                    f"CSV file is missing one of the required columns: {required_columns}"
                )
            return list(reader)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []
    except ValueError as e:
        print(f"Error: {e}")
        return []


# --- TRANSFORMATION FUNCTIONS ---


def get_unique_genres(movie_list: list) -> set:
    """
    Extracts all unique genres, ignoring the placeholder '(no genres listed)'.
    """
    unique_genres = set()
    for movie in movie_list:
        genres = movie["genres"].split("|")
        for genre in genres:
            if genre != "(no genres listed)":
                unique_genres.add(genre)
    return unique_genres


def transform_movie_records(movie_list: list) -> list:
    """
    Cleans and transforms movie records by casting 'movieId' to an integer
    and separating 'title' from 'year'.
    """
    transformed_list = []
    for movie in movie_list:
        match = re.search(r"\((\d{4})\)$", movie["title"])
        year = int(match.group(1)) if match else None
        title = re.sub(r"\s*\(\d{4}\)$", "", movie["title"]).strip()

        transformed_list.append(
            {
                "movieId": int(movie["movieId"]),
                "title": title,
                "year": year,
                "genres": movie["genres"].split("|"),
            }
        )
    return transformed_list


# --- SAVING FUNCTIONS ---


def save_to_json(data: list, file_path: Path):
    """Saves a list of dictionaries to a JSON file."""
    with open(file_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def save_to_txt(data: set, file_path: Path):
    """Saves a set to a text file, with one item per line."""
    with open(file_path, mode="w", encoding="utf-8") as f:
        for item in sorted(list(data)):
            f.write(f"{item}\n")


def save_to_csv(data: list, file_path: Path, headers: list):
    """Saves a list of dictionaries or tuples to a CSV file."""
    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


# --- Main execution block ---
if __name__ == "__main__":

    print("Loading and validating raw movie data...")
    movies_raw = load_movie_data(config.MOVIES_RAW_DIR)

    if movies_raw:
        print("Transforming data...")
        unique_genres = get_unique_genres(movies_raw)
        transformed_movies = transform_movie_records(movies_raw)
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
        print(f"Saving processed files to {config.PROCESSED_DATA_DIR}...")

        save_to_json(
            transformed_movies,
            config.MOVIES_CLEANED_DIR,
        )

        save_to_txt(unique_genres, config.UNIQUE_GENRES_DIR)

        movies_for_csv = [
            {"movieId": m["movieId"], "title": m["title"], "year": m["year"]}
            for m in transformed_movies
        ]
        save_to_csv(
            movies_for_csv,
            config.MOVIE_ID_TITLE_YEAR_DIR,
            headers=["movieId", "title", "year"],
        )

        print("Process complete! All three files have been generated.")
