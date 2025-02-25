import pandas as pd
from fpgrowth_py import fpgrowth
import pickle
import os

def generate_rules_fpgrowth(dataset_path, minSupRatio=0.01, minConf=0.5):
    print("Reading dataset from:", dataset_path)
    df = pd.read_csv(dataset_path)
    print("Dataset loaded. Number of rows:", len(df))
    
    print("Grouping data by 'pid' to create baskets of track names.")
    baskets = df.groupby('pid')['track_name'].apply(list).tolist()
    print("Number of baskets created:", len(baskets))
    
    # Check if there are at least 2 baskets to generate frequent itemsets
    if len(baskets) < 2:
        print("Not enough baskets to generate frequent item sets. Need at least 2, got", len(baskets))
        return [], []
    
    print("Running FP-Growth with minSupRatio =", minSupRatio, "and minConf =", minConf)
    result = fpgrowth(baskets, minSupRatio=minSupRatio, minConf=minConf)
    if result is None:
        print("No frequent item set found with the given thresholds.")
        freqItemSet, rules = [], []
    else:
        freqItemSet, rules = result
        print("FP-Growth complete. Number of rules generated:", len(rules))
    return freqItemSet, rules

def main():
    dataset_path = os.getenv("DATASET_PATH", "/home/datasets/spotify/2023_spotify_ds1.csv")
    print("Starting FP-Growth model generation process...")
    freqItemSet, rules = generate_rules_fpgrowth(dataset_path)
    print("Generated rules:")
    print(rules)
    
    model_dir = "/app/model"
    print("Ensuring that the model directory exists at:", model_dir)
    os.makedirs(model_dir, exist_ok=True)
    
    model_file_path = os.path.join(model_dir, "model_rules.pickle")
    print("Saving model to:", model_file_path)
    with open(model_file_path, "wb") as f:
        # Save both frequent item sets and rules
        pickle.dump((freqItemSet, rules), f)
    print("Model successfully saved to", model_file_path)

if __name__ == "__main__":
    main()
