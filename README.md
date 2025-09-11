# 🚀 de-learning-project

A data engineering learning project to build a complete data pipeline using Python, SQL and Airflow.

---
## 🏁 Getting Started

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

First, clone this repository to your local machine.
```bash
git clone [https://github.com/jbalcucho/de-learning-project.git](https://github.com/jbalcucho/de-learning-project.git)
cd de-learning-project
```

### 2. 📥 Download Data
This project uses the MovieLens (small) dataset. A shell script is provided to automatically download and set up the data.

From the project's root directory, run the following command to download the data into the data/raw/ folder:

#### Make the script executable (only needs to be done once)
First, clone this repository to your local machine.
```bash
chmod +x scripts/download_data.sh
```

#### Run the script to download and prepare the data
```bash
./scripts/download_data.sh
```

### 3. Create Virtual environment
Next, set up a Python virtual environment to manage project dependencies.

Create the environment:

```bash
python3 -m venv venv
```

Activate the environment:

On macOS and Linux:

Bash

```bash
source venv/bin/activate
```

On Windows:

```bash
.\venv\Scripts\activate
```
Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. 🧪 Running Tests
This project uses pytest for unit testing. The tests ensure that the data processing logic is working correctly and helps prevent regressions.

To run the tests, make sure your virtual environment is activated and then run the following command from the project's root directory:

```bash
python -m pytest
```

### 5. 🚀 Running the API

This project includes a basic Flask API to serve the processed movie data.

### 5.1. Run the API Server

Make sure your virtual environment is activated, then run the following command from the project's root directory to start the server:

```bash
python src/api.py
```

The server will start and be available at http://127.0.0.1:5001.

### 5.2. Consume the Endpoint
Open a new terminal window and use a tool like curl to send a request to the API. For example, to get the 5 most recent "Action" movies:

```bash
curl "[http://127.0.0.1:5001/api/movies/top_by_genre?genre=Action&top_n=5](http://127.0.0.1:5001/api/movies/top_by_genre?genre=Action&top_n=5)"
```
You will receive a JSON response with the requested movie data.

### 6.  📊 Generating Analysis Plots

This project includes a script to perform basic analysis and generate visualizations from the cleaned data.

To generate the plot, ensure your virtual environment is activated and run the following command from the project's root directory:

```bash
python src/analysis.py
```
This will create a bar chart of the top 10 movie genres and save it as a PNG image in the reports/figures/ directory.