from flask import Flask, request, jsonify
import pickle
import os
import time

app = Flask(__name__)

# Path to the ML model (rules) stored on the shared volume
MODEL_PATH = "/app/model/model_rules.pickle"
MODEL_VERSION = "0.1"

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return None

# Initial model load and timestamp
model = load_model()
last_model_mtime = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

@app.route("/api/recommend", methods=["POST"])
def recommend():
    global model, last_model_mtime
    # Check if the model file has been updated and reload if necessary
    if os.path.exists(MODEL_PATH):
        current_mtime = os.path.getmtime(MODEL_PATH)
        if last_model_mtime is None or current_mtime > last_model_mtime:
            model = load_model()
            last_model_mtime = current_mtime
            app.logger.info("Model reloaded due to file change.")

    data = request.get_json(force=True)
    user_songs = data.get("songs", [])
    
    recommended = []
    if model is not None:
        # For each rule, if the antecedents are a subset of user_songs, add consequents to recommendations
        for _, row in model.iterrows():
            if set(row['antecedents']).issubset(user_songs):
                for song in row['consequents']:
                    if song not in user_songs and song not in recommended:
                        recommended.append(song)
    
    response = {
        "songs": recommended,
        "version": MODEL_VERSION,
        "model_date": time.ctime(last_model_mtime) if last_model_mtime else "Unknown"
    }
    return jsonify(response)

if __name__ == "__main__":
    # Run the app on port 5000, accessible from any network interface
    app.run(host="0.0.0.0", port=5000, debug=True)
