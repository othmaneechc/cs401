import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pickle
import os

def generate_rules(dataset_path, min_support=0.01, min_confidence=0.5):
    # Read the CSV file (adjust the path as needed)
    df = pd.read_csv(dataset_path)
    
    # Group by playlist id ('pid') and create baskets of track names
    baskets = df.groupby('pid')['track_name'].apply(list).tolist()
    
    # One-hot encode the baskets
    te = TransactionEncoder()
    te_array = te.fit(baskets).transform(baskets)
    df_hot = pd.DataFrame(te_array, columns=te.columns_)
    
    # Compute frequent itemsets using Apriori and generate association rules
    freq_items = apriori(df_hot, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric="confidence", min_threshold=min_confidence)
    return rules

if __name__ == "__main__":
    # Ensure that the dataset file exists on the node at this location
    dataset_path = "/home/datasets/spotify/2023_spotify_ds2.csv"
    rules = generate_rules(dataset_path)
    print("Generated rules:")
    print(rules)
    
    # Save the model (rules) to a directory that will be shared with the API
    model_dir = "/app/model"
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "model_rules.pickle"), "wb") as f:
        pickle.dump(rules, f)
    print("Model saved to /app/model/model_rules.pickle")
