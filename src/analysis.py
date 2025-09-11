# src/analysis.py
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_cleaned_data(file_path: str) -> pd.DataFrame:
    """Loads the cleaned movie data from a JSON file into a pandas DataFrame."""
    try:
        return pd.read_json(file_path)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        print("Please run 'python src/ingestion.py' first to generate it.")
        return None

def generate_genre_distribution_plot(df: pd.DataFrame, output_path: str):
    """
    Generates and saves a bar chart of the top 10 movie genres.
    """
    if df is None or df.empty:
        print("DataFrame is empty. Cannot generate plot.")
        return

    # 1. Count genre occurrences
    # 'explode' transforms each element of a list-like to a row
    genre_counts = df['genres'].explode().value_counts()
    
    # 2. Select top 10
    top_10_genres = genre_counts.head(10)

    # 3. Create the plot
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(10, 7))
    
    top_10_genres.sort_values().plot(kind='barh', ax=ax, color='skyblue')
    
    ax.set_title('Top 10 Most Common Movie Genres', fontsize=16)
    ax.set_xlabel('Number of Movies', fontsize=12)
    ax.set_ylabel('Genre', fontsize=12)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 4. Save the plot to a file
    plt.savefig(output_path, bbox_inches='tight')
    print(f"✅ Plot saved successfully to {output_path}")
    plt.close(fig)


if __name__ == "__main__":
    CLEANED_DATA_FILE = "data/processed/movies_cleaned.json"
    PLOT_OUTPUT_FILE = "reports/figures/genre_distribution.png"
    
    # Load data
    movies_df = load_cleaned_data(CLEANED_DATA_FILE)
    
    # Generate and save the plot
    if movies_df is not None:
        generate_genre_distribution_plot(movies_df, PLOT_OUTPUT_FILE)