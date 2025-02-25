from flask import Flask, request, jsonify
import pickle
import os
from flask_cors import CORS
import time

CORS(app)  # This will enable CORS for all routes
app = Flask(__name__)
MODEL_PATH = "/app/model/model_rules.pickle"
MODEL_VERSION = "0.1"

# Load the model and extract rules
def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model_data = pickle.load(f)
        # model_data is a tuple: (freqItemSet, rules)
        return model_data[1]  # return rules only
    return None

# Initially load the model rules and record modification time
model_rules = load_model()
last_model_mtime = os.path.getmtime(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

@app.route("/api/recommend", methods=["POST"])
def recommend():
    global model_rules, last_model_mtime
    # Check if the model file has been updated
    if os.path.exists(MODEL_PATH):
        current_mtime = os.path.getmtime(MODEL_PATH)
        if last_model_mtime is None or current_mtime > last_model_mtime:
            model_rules = load_model()
            last_model_mtime = current_mtime
            app.logger.info("Model reloaded due to file change.")

    data = request.get_json(force=True)
    user_songs = data.get("songs", [])
    recommended = []
    
    # model_rules is a list of rules, where each rule is [antecedents, consequents, confidence]
    if model_rules:
        for rule in model_rules:
            antecedents, consequents, conf = rule
            if set(antecedents).issubset(user_songs):
                for song in consequents:
                    if song not in user_songs and song not in recommended:
                        recommended.append(song)
    else:
        app.logger.error("No model rules loaded.")
    
    response = {
        "songs": recommended,
        "version": MODEL_VERSION,
        "model_date": time.ctime(last_model_mtime) if last_model_mtime else "Unknown"
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
