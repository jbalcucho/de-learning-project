import os
import config
import pandas as pd


def create_movie_analytics():
    """
    Loads processed movie and raw ratings data, calculates analytics,
    and saves the result to the gold data layer.
    """

    os.makedirs(config.GOLD_DATA_DIR, exist_ok=True)

    movies_df = pd.read_json(config.MOVIES_CLEANED_DIR)
    ratings_df = pd.read_csv(config.RATINGS_RAW_DIR)

    ratings_summary = (
        ratings_df.groupby("movieId")["rating"]
        .agg(average_rating="mean", num_ratings="count")
        .reset_index()
    )

    movie_analytics_df = pd.merge(movies_df, ratings_summary, on="movieId", how="inner")

    filtered_analytics_df = movie_analytics_df[
        movie_analytics_df["num_ratings"] > 10
    ].copy()

    filtered_analytics_df["average_rating"] = filtered_analytics_df[
        "average_rating"
    ].round(2)

    print(f"Saving final analytics file to {config.MOVIE_ANALYTICS_DIR}...")

    filtered_analytics_df.to_csv(config.MOVIE_ANALYTICS_DIR, index=False)

    print("\nGold layer processing complete!")
    print(f"Total movies with >10 ratings: {len(filtered_analytics_df)}")


if __name__ == "__main__":
    create_movie_analytics()
