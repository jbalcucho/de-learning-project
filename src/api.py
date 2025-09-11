# src/api.py
from flask import Flask, jsonify, request
import pandas as pd

# Create the Flask application object
app = Flask(__name__)

# --- Load data once when the app starts ---
DATA_FILE = "data/processed/movies_cleaned.json"
try:
    print("Loading data for the API...")
    movies_df = pd.read_json(DATA_FILE)
    # Convert year to a numeric type that can handle NaNs, then to integer
    movies_df["year"] = pd.to_numeric(movies_df["year"], errors="coerce").astype(
        "Int64"
    )
    print("✅ Data loaded successfully.")
except FileNotFoundError:
    print(f"⚠️  Warning: Data file not found at {DATA_FILE}. API endpoints may fail.")
    movies_df = pd.DataFrame()  # Create an empty DataFrame


# --- API Endpoints ---


@app.route("/")
def index():
    """A simple index route to show the API is running."""
    return "<h1>Movie Data API</h1><p>Welcome! Try the /api/movies/top_by_genre endpoint.</p>"


@app.route("/api/movies/top_by_genre", methods=["GET"])
def get_top_movies_by_genre():
    """
    Returns the top N most recent movies for a given genre.
    Query parameters:
        - genre (str, required): The genre to filter by (e.g., 'Action', 'Comedy').
        - top_n (int, optional): The number of movies to return. Defaults to 10.
    """
    # Get query parameters from the request URL
    genre = request.args.get("genre")
    try:
        top_n = int(request.args.get("top_n", 10))
    except (ValueError, TypeError):
        return (
            jsonify({"error": "Invalid 'top_n' parameter. It must be an integer."}),
            400,
        )

    if not genre:
        return jsonify({"error": "A 'genre' query parameter is required."}), 400

    if movies_df.empty:
        return jsonify({"error": "Movie data is not available."}), 500

    # Filter the DataFrame
    # We use 'explode' to handle the list of genres in each row
    genre_df = movies_df.explode("genres")
    filtered_movies = genre_df[genre_df["genres"].str.lower() == genre.lower()]

    if filtered_movies.empty:
        return jsonify({"message": f"No movies found for genre '{genre}'."}), 404

    # Sort by year (newest first) and take the top N
    top_movies = filtered_movies.sort_values(by="year", ascending=False).head(top_n)

    # Convert the result to a JSON-friendly format (list of dictionaries)
    result = top_movies.to_dict(orient="records")

    return jsonify(result)


if __name__ == "__main__":
    # Run the app in debug mode, which is useful for development
    app.run(debug=True, port=5001)
