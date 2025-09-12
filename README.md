# Movie Data Pipeline Project 🚀
This project demonstrates a complete, multi-layered data engineering pipeline. It ingests raw data from the MovieLens dataset, processes it through several layers of transformation and analysis, and exposes the results via a Flask API.

## 🏛️ Project Architecture

The pipeline is structured around a multi-layered data architecture, where data is progressively cleaned, enriched, and aggregated.

Data Flow:

- Raw Layer (data/raw/): The original, unchanged data downloaded from the source.

- Processed Layer (data/processed/): Data that has been cleaned, validated, and transformed into a consistent format (e.g., movies_cleaned.json). This is the "single source of truth."

- Gold Layer (data/gold/): Aggregated data ready for analytics and business intelligence (e.g., movie_analytics.csv).

## 🏁 Getting Started
Follow these steps to set up and run the project on your local machine.

1. Clone the Repository
git clone [https://github.com/jbalcucho/de-learning-project.git](https://github.com/jbalcucho/de-learning-project.git)

2. Download the Data
A shell script is provided to automatically download the MovieLens (small) dataset into the data/raw/ folder. Make the script executable (only needs to be done once)

    ```
    chmod +x scripts/download_data.sh
    ```

3. Run the script
    ```
    ./scripts/download_data.sh
    ```

4. Set Up the Environment
Create and activate a Python virtual environment to manage dependencies.
    - Create the environment
        ```
        python3 -m venv venv
        ```

    - Activate the environment (macOS/Linux)
        ```
        source venv/bin/activate
        ```

    - Or activate on Windows
        ```
        .\venv\Scripts\activate
        ```

    - Install the required packages
        ```
        pip install -r requirements.txt
        ```



## ⚙️ Project Workflow

Run the data pipeline scripts in the following order to process the data from the raw to the gold layer.

Step 1: Run the Ingestion Script (Raw → Processed)
This script loads the raw movies.csv, cleans it, and saves the transformed data.

Command:

```
python src/ingestion.py
```
Input: 
- data/raw/movies.csv

Output: 
- data/processed/movies_cleaned.json
- data/processed/unique_genres.txt

Step 2: Run the Processing Script (Processed → Gold)
This script loads the cleaned movie data and raw ratings, calculates analytics (like average rating and number of ratings), and saves the aggregated result.

Command:

```
python src/processing.py
```

Input: 
- data/processed/movies_cleaned.json
- data/raw/ratings.csv

Output: 
- data/gold/movie_analytics.csv

Step 3: Generate Analysis Plots
This script uses the processed data to generate a visualization of the top movie genres.

Command:
```
python src/analysis.py
```

Input: 
- data/processed/movies_cleaned.json

Output: 
- A plot saved in reports/figures/


## 🚀 Running the API

The Flask API serves the processed and aggregated data. Ensure you have completed the project workflow steps above before running the API.
1. Start the API Server. 

    Run the following command from the project's root directory:
    ```
    python src/api.py
    ```

    The server will be available at http://127.0.0.1:5001.

2. API Endpoints

    You can use a tool like curl or a web browser to interact with the endpoints.

    `GET /api/movies/top_by_genre`

    Returns the top N most recent movies for a given genre.
    - genre (required): The genre to filter by (e.g., Action).
    - top_n (optional): The number of movies to return (defaults to 10).

    Example:
    
    [http://127.0.0.1:5001/api/movies/top_by_genre?genre=Action&top_n=5](http://127.0.0.1:5001/api/movies/top_by_genre?genre=Action&top_n=5)


    `GET /api/movies/recommend`

    Recommends a single random movie based on high ratings (avg_rating > 4.0, num_ratings > 50).
    - genre (optional): Further filter the recommendation by a specific genre.
    
    Example (any genre):
    
    [http://127.0.0.1:5001/api/movies/recommend](http://127.0.0.1:5001/api/movies/recommend)


    Example (filtered by genre):

    [http://127.0.0.1:5001/api/movies/recommend?genre=Sci-Fi](http://127.0.0.1:5001/api/movies/recommend?genre=Sci-Fi)


## 🧪 Running Tests

This project uses pytest for unit testing. To run the tests, execute the following command from the project's root directory:
python -m pytest


## Project Structure
```
.
├── data
│   ├── gold/ 
│   ├── processed/
│   └── raw/
├── reports
│   └── figures/
├── scripts
│   └── download_data.sh
├── src
│   ├── __init__.py
│   ├── analysis.py
│   ├── api.py
│   ├── config.py
│   ├── ingestion.py
│   └── processing.py
├── tests
│   ├── __init__.py
│   └── test_ingestion.py
├── .gitignore
├── README.md
└── requirements.txt
```