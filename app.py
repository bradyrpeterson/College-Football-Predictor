from flask import Flask, render_template, request
from predictor import predict_game, ratings  # imports your model + function
import requests
import os
import json

app = Flask(__name__)

# --- Get FBS team list from CollegeFootballData API ---
# --- Get FBS team list, using cache if available ---
with open("fbs_teams_2025.json","r") as f:
    fbs_teams=json.load(f)

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
            result = f"{winner} has a {winner_prob*100:.2f}% chance to win and is predicted to win by {abs(margin):.2f}"
        except KeyError:
            result = "One of those teams isn't available in the dataset."

    return render_template("index.html", teams=fbs_teams, result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")