import requests

API_URL = "http://localhost:52001/api/recommend"

def get_recommendations(songs):
    data = {"songs": songs}
    response = requests.post(API_URL, json=data)
    if response.status_code == 200:
        print("Recommendations:", response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    get_recommendations(["Yesterday", "Bohemian Rhapsody"])
