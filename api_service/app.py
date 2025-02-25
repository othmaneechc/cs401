from flask import Flask, request, jsonify, render_template
import pickle
import os
import csv
import random

app = Flask(__name__)

# Define paths for the model and songs dataset.
MODEL_PATH = "/app/model/model_rules.pickle"
SONGS_DATASET_PATH = "/app/model/2023_spotify_songs.csv"

# Load the association rules model (frequent item sets and rules)
try:
    with open(MODEL_PATH, "rb") as f:
        freqItemSet, rules = pickle.load(f)
    app.rules = rules
    print(f"Loaded model with {len(rules)} rules.")
except Exception as e:
    app.rules = []
    print("Error loading model:", e)

# Load the full songs dataset from CSV.
def load_songs_dataset(file_path):
    songs = []
    try:
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # Try to read the 'song' field; fallback to the first column if not present.
            for row in reader:
                if "track_name" in row:
                    songs.append(row["track_name"])
                else:
                    # Fallback: use first column value
                    songs.append(list(row.values())[1])
    except Exception as e:
        print("Error loading songs dataset:", e)
    return songs

app.songs_dataset = load_songs_dataset(SONGS_DATASET_PATH)
print(f"Loaded songs dataset with {len(app.songs_dataset)} songs.")

# Define version and model_date for display purposes.
app.version = "0.1"
app.model_date = "2023-04-01"  # Update accordingly

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json(force=True)
    input_songs = data.get("songs", [])
    
    # Normalize input: lowercase and strip whitespace.
    input_set = set(song.strip().lower() for song in input_songs if song.strip())
    
    if not input_set:
        return jsonify({
            "error": "No input songs provided.",
            "version": app.version,
            "model_date": app.model_date
        }), 400

    recommended = set()
    
    # Use association rules: for each rule, if the rule's antecedent is a subset
    # of the user's input, add the consequent to recommendations.
    for rule in app.rules:
        antecedent, consequent, conf = rule
        antecedent_lower = set(item.lower() for item in antecedent)
        if antecedent_lower.issubset(input_set):
            consequent_lower = set(item.lower() for item in consequent)
            recommended.update(consequent_lower)
    
    # Remove any songs that the user already provided.
    recommended = recommended - input_set

    # If recommendations from rules are insufficient (e.g., less than 3 songs),
    # supplement with additional songs from the full songs dataset.
    desired_recommendation_count = 3
    if len(recommended) < desired_recommendation_count:
        # Normalize full songs dataset to lowercase for matching.
        all_songs = set(song.strip()for song in app.songs_dataset)
        # Exclude songs already in input or already recommended.
        available_songs = list(all_songs - input_set - recommended)
        needed = desired_recommendation_count - len(recommended)
        if available_songs:
            supplemental = random.sample(available_songs, min(needed, len(available_songs)))
            recommended.update(supplemental)

    # Final recommendations list.
    recommendations_list = list(recommended)
    message = None if recommendations_list else "No recommendations found based on the input songs."

    return jsonify({
        "songs": recommendations_list,
        "message": message,
        "version": app.version,
        "model_date": app.model_date
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
