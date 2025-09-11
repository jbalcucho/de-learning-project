#!/bin/bash

# This script downloads the MovieLens (small) dataset and prepares it in the data/raw folder.
# use this command to give permissions:
# chmod +x scripts/download_data.sh

# Dataset URL
URL="https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

# Target directory for raw data
RAW_DATA_DIR="data/raw"
ZIP_FILE="$RAW_DATA_DIR/movielens.zip"

# 1. Create the directory if it doesn't exist
echo "⚙️  Creating directory $RAW_DATA_DIR..."
mkdir -p $RAW_DATA_DIR

# 2. Download the ZIP file
echo "📥  Downloading dataset from $URL..."
curl -L $URL -o $ZIP_FILE

# 3. Unzip the contents
echo "📦  Unzipping file into $RAW_DATA_DIR..."
unzip -o $ZIP_FILE -d $RAW_DATA_DIR

# 4. Move the CSV files to the raw root and clean up
# The zip creates a 'ml-latest-small' folder. We move its contents and then delete it.
EXTRACTED_DIR="$RAW_DATA_DIR/ml-latest-small"
if [ -d "$EXTRACTED_DIR" ]; then
    echo "🧹  Cleaning up and organizing files..."
    mv $EXTRACTED_DIR/*.csv $RAW_DATA_DIR/
    rm -rf $EXTRACTED_DIR
    rm $ZIP_FILE
else
    echo "⚠️  Extracted directory not found as expected. You may need to move the files manually."
fi

echo "✅  Process complete! Data is ready in $RAW_DATA_DIR."