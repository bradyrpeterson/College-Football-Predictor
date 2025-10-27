from flask import Flask, render_template, request
from predictor import predict_game, ratings  # imports your model + function
import requests
import os
import json

app = Flask(__name__)

#Get the FBS Teams from the json file
with open("fbs_teams_2025.json","r") as f:
    fbs_teams=json.load(f)

#Get the team logos from the other json file
with open("team_logos.json", "r") as f:
    team_logos = json.load(f)

@app.route("/", methods=["GET", "POST"])
def home():
    #New with logos - Instantiate all the variables first
    result = None
    home_team= None
    away_team = None
    home_logo = None
    away_logo = None
    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]

        
        margin, prob = predict_game(home_team, away_team)
        winner = home_team if margin > 0 else away_team
        if(margin>0):
             winner_prob=prob
        else: winner_prob=1-prob
        result = f"{winner} has a {winner_prob*100:.2f}% chance to win and is predicted to win by {abs(margin):.2f}"
        
        home_logo = team_logos.get(home_team)
        away_logo = team_logos.get(away_team)

    return render_template("index.html", teams=fbs_teams, result=result,home_team=home_team,away_team=away_team,home_logo=home_logo,away_logo=away_logo)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")