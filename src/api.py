# src/api.py
import config
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- Load data once when the app starts ---
try:
    movies_df = pd.read_json(config.MOVIES_CLEANED_DIR)
    movies_df["year"] = pd.to_numeric(movies_df["year"], errors="coerce").astype(
        "Int64"
    )
    print("Movie data loaded successfully.")
except FileNotFoundError:
    print(f"Warning: Clean movie data file not found. Some endpoints may fail.")
    movies_df = pd.DataFrame()

try:
    analytics_df = pd.read_csv(config.MOVIE_ANALYTICS_DIR)
    print("Movie analytics data loaded successfully.")
except FileNotFoundError:
    print(f"Warning: Analytics data file not found. Recommendation endpoint will fail.")
    analytics_df = pd.DataFrame()


# --- API Endpoints ---


@app.route("/")
def index():
    """A simple index route to show the API is running."""
    return "<h1>Movie Data API</h1><p>Welcome! Explore the available endpoints.</p>"


@app.route("/api/movies/top_by_genre", methods=["GET"])
def get_top_movies_by_genre():
    """
    Returns the top N most recent movies for a given genre.
    Query parameters:
        - genre (str, required): The genre to filter by (e.g., 'Action', 'Comedy').
        - top_n (int, optional): The number of movies to return. Defaults to 10.
    """
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

    # We use 'explode' to handle the list of genres in each row
    genre_df = movies_df.explode("genres")
    filtered_movies = genre_df[genre_df["genres"].str.lower() == genre.lower()]

    if filtered_movies.empty:
        return jsonify({"message": f"No movies found for genre '{genre}'."}), 404

    top_movies = filtered_movies.sort_values(by="year", ascending=False).head(top_n)
    result = top_movies.to_dict(orient="records")
    return jsonify(result)


@app.route("/api/movies/recommend", methods=["GET"])
def get_recommendation():
    """
    Recommends a single random movie based on high ratings and an optional genre.
    Filters for movies with an average rating > 4.0 and more than 50 ratings.
    """
    if analytics_df.empty:
        return jsonify({"error": "Analytics data is not available."}), 500

    highly_rated_movies = analytics_df[
        (analytics_df["average_rating"] > 4.0) & (analytics_df["num_ratings"] > 50)
    ].copy()

    genre = request.args.get("genre")
    if genre:
        highly_rated_movies["genres"] = highly_rated_movies["genres"].apply(eval)
        genre_df = highly_rated_movies.explode("genres")
        filtered_movies = genre_df[genre_df["genres"].str.lower() == genre.lower()]
    else:
        filtered_movies = highly_rated_movies

    if filtered_movies.empty:
        return jsonify({"message": "No movies match the specified criteria."}), 404

    recommendation = filtered_movies.sample(n=1)
    result = recommendation.to_dict(orient="records")[0]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
