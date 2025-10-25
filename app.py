from flask import Flask, render_template, request
from predictor import predict_game, ratings  # imports your model + function
import requests
import os
import json

app = Flask(__name__)

# --- Get FBS team list from CollegeFootballData API ---
# --- Get FBS team list, using cache if available ---
CACHE_FILE = "fbs_teams_2025.json"

if os.path.exists(CACHE_FILE):
    # Load from local cache
    with open(CACHE_FILE, "r") as f:
        fbs_teams = json.load(f)
else:
    #If the list isn't cached call the API
    headers = {
        "Authorization": "Bearer API_KEY"
    }
    teams_url = "https://api.collegefootballdata.com/teams/fbs?year=2025"
    response = requests.get(teams_url, headers=headers)

    if response.ok:
        fbs_teams = sorted([team["school"] for team in response.json()])
        # Save list to cache for next time
        with open(CACHE_FILE, "w") as f:
            json.dump(fbs_teams, f)
        print(f"Cached {len(fbs_teams)} FBS teams to {CACHE_FILE}")
    else:
        print("Warning: API request failed, using fallback team list.")
        fbs_teams = sorted(ratings.index)

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]

        try:
            margin, prob = predict_game(home_team, away_team)
            winner = home_team if margin > 0 else away_team
            if(margin>0):
                winner_prob=prob
            else: winner_prob=1-prob
            result = f"{winner} has a {winner_prob:.2f}% chance to win and is predicted to win by {abs(margin):.2f}"
        except KeyError:
            result = "One of those teams isn't available in the dataset."

    return render_template("index.html", teams=fbs_teams, result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")