from flask import Flask, request, jsonify, render_template
import pickle
import os
import csv
import random

app = Flask(__name__)

# Helper function to normalize song names
def normalize(text):
    return text.strip().lower()

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
            # Try to read the 'track_name' field; fallback to the second column if not present.
            for row in reader:
                if "track_name" in row:
                    songs.append(row["track_name"])
                else:
                    songs.append(list(row.values())[1])
    except Exception as e:
        print("Error loading songs dataset:", e)
    return songs

app.songs_dataset = load_songs_dataset(SONGS_DATASET_PATH)
print(f"Loaded songs dataset with {len(app.songs_dataset)} songs.")

# Build a mapping for normalized song name to original formatting.
app.songs_mapping = {normalize(song): song.strip() for song in app.songs_dataset}

# Helper function to get the original song title from a normalized version.
def get_original_song(normalized_song):
    original = app.songs_mapping.get(normalized_song)
    if original:
        return original
    for song in app.songs_dataset:
        if normalize(song) == normalized_song:
            return song.strip()
    return normalized_song

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
    input_set = set(normalize(song) for song in input_songs if song)
    
    if not input_set:
        return jsonify({
            "error": "No input songs provided.",
            "version": app.version,
            "model_date": app.model_date
        }), 400

    recommended = set()
    rule_found = False  # Track if any rule matches the input

    # Use association rules: check if any rule's antecedent is a subset of input.
    for rule in app.rules:
        antecedent, consequent, conf = rule
        antecedent_normalized = set(normalize(item) for item in antecedent)
        if antecedent_normalized.issubset(input_set):
            rule_found = True
            recommended.update(set(normalize(item) for item in consequent))
    
    # Remove songs that the user already provided.
    recommended = recommended - input_set

    desired_recommendation_count = 3
    message = None

    if not rule_found:
        # No rules matched; return 3 random songs from the full dataset.
        all_songs = set(normalize(song) for song in app.songs_dataset)
        available_songs = list(all_songs - input_set)
        if available_songs:
            recommended = set(random.sample(available_songs, min(desired_recommendation_count, len(available_songs))))
        message = "No direct recommendations found. Here are 3 random recommendations:"
    else:
        # If there are rule-based recommendations but fewer than desired, supplement with random songs.
        if len(recommended) < desired_recommendation_count:
            all_songs = set(normalize(song) for song in app.songs_dataset)
            available_songs = list(all_songs - input_set - recommended)
            needed = desired_recommendation_count - len(recommended)
            if available_songs:
                recommended.update(random.sample(available_songs, min(needed, len(available_songs))))

    # Map normalized recommendations back to their original formatting.
    recommendations_list = [get_original_song(song) for song in recommended]
    if not recommendations_list:
        message = "No recommendations found based on the input songs."

    return jsonify({
        "songs": recommendations_list,
        "message": message,
        "version": app.version,
        "model_date": app.model_date
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
